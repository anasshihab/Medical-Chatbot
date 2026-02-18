"""Chat API endpoint with streaming support and 6-hour usage gating"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
from app.database import get_db
from app.schemas.chat import ChatRequest
from app.models.user import User
from app.models.guest_session import GuestSession
from app.models.conversation import Conversation
from app.models.message import Message
from app.dependencies import get_current_user
from app.agent.agent import MedicalChatAgent
from app.core.plans import check_plan_limit, check_word_limit
from app.core.usage import (
    increment_user_usage,
    increment_guest_usage,
    get_or_create_guest_session,
    check_and_reset_user_window,
    check_and_reset_guest_window,
)
from app.utils.constants import PlanType, PLAN_LIMITS

router = APIRouter(prefix="/api", tags=["Chat"])
import logging
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with streaming support.

    Supports both authenticated users and guest sessions.
    Enforces:
      - 6-hour rolling window question limits (Guest: 2, Free: 5, Pro: unlimited)
      - Per-message word limits (Guest: 20 words, Free: 25 words, Pro: 1000 words)
    """
    # ── 1. Identify caller ────────────────────────────────────────────────────
    user_id = None
    guest_session = None
    plan_type = PlanType.FREE

    if current_user:
        user_id = current_user.id
        plan_type = current_user.plan_type
        # Reset window if 6 hours have elapsed
        check_and_reset_user_window(db, current_user)
        question_count = current_user.question_count
        last_reset_at = current_user.last_reset_at

    elif request.guest_session_id:
        guest_session = get_or_create_guest_session(db, request.guest_session_id)
        plan_type = PlanType.GUEST
        # Reset window if 6 hours have elapsed
        check_and_reset_guest_window(db, guest_session)
        question_count = guest_session.question_count
        last_reset_at = guest_session.last_reset_at

    else:
        from app.utils.errors import UnauthorizedException
        raise UnauthorizedException("Authentication or guest session ID required")

    # ── 2. Word-count validation (HTTP 400) ───────────────────────────────────
    check_word_limit(request.message, plan_type)

    # ── 3. 6-hour window limit check (HTTP 403) ───────────────────────────────
    check_plan_limit(question_count, plan_type, last_reset_at)

    # ── 4. Get or create conversation ─────────────────────────────────────────
    conversation = None
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()

        if not conversation:
            from app.utils.errors import NotFoundException
            raise NotFoundException("Conversation")
    else:
        conversation = Conversation(
            user_id=user_id,
            guest_session_id=guest_session.id if guest_session else None
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # ── 5. Load conversation history ──────────────────────────────────────────
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    # ── 6. Save user message ──────────────────────────────────────────────────
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    logger.info(f"User Input (ConvID: {conversation.id}): {request.message}")

    # ── 7. Increment usage counters ───────────────────────────────────────────
    if current_user:
        increment_user_usage(db, current_user.id)
    else:
        increment_guest_usage(db, guest_session.id)

    # ── 8. Process with agent ─────────────────────────────────────────────────
    agent = MedicalChatAgent()

    attachments_data = None
    if request.attachments:
        attachments_data = [
            {
                "file_data": att.file_data,
                "file_type": att.file_type,
                "file_name": att.file_name,
                "file_size": att.file_size
            }
            for att in request.attachments
        ]

    async def event_stream():
        """Stream events to client"""
        assistant_message_content = ""
        metadata = {}

        request_total_cost = 0.0
        request_total_input_tokens = 0
        request_total_output_tokens = 0
        request_cost_breakdown = []

        try:
            async for chunk in agent.process_message(request.message, conversation_history, attachments_data):
                if chunk["type"] == "content":
                    assistant_message_content += chunk["data"]
                    yield f"data: {json.dumps(chunk)}\n\n"

                elif chunk["type"] == "metadata":
                    metadata.update(chunk["data"])
                    yield f"data: {json.dumps(chunk)}\n\n"

                elif chunk["type"] == "done":
                    metadata.update(chunk["data"])

                    request_total_cost = chunk["data"].get("total_cost", 0.0)
                    request_total_input_tokens = chunk["data"].get("total_input_tokens", 0)
                    request_total_output_tokens = chunk["data"].get("total_output_tokens", 0)
                    request_cost_breakdown = chunk["data"].get("cost_breakdown", [])

                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=assistant_message_content,
                        meta_data=metadata
                    )

                    logger.info(f"Assistant Output (ConvID: {conversation.id}): {assistant_message_content[:200]}...")
                    db.add(assistant_message)

                    if not conversation.title:
                        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")

                    db.commit()
                    db.refresh(assistant_message)

                    if request_total_cost > 0:
                        from app.utils.cost_calculator import log_grand_total_cost
                        log_grand_total_cost(
                            total_cost=request_total_cost,
                            total_input_tokens=request_total_input_tokens,
                            total_output_tokens=request_total_output_tokens,
                            step_breakdown=request_cost_breakdown
                        )

                    final_chunk = {
                        "type": "done",
                        "data": {
                            **chunk["data"],
                            "conversation_id": conversation.id,
                            "message_id": assistant_message.id
                        }
                    }
                    yield f"data: {json.dumps(final_chunk)}\n\n"

        except Exception as e:
            error_chunk = {
                "type": "error",
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
