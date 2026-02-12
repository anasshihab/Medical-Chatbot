"""Chat API endpoint with streaming support"""
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
from app.core.plans import check_plan_limit
from app.core.usage import increment_user_usage, increment_guest_usage, get_or_create_guest_session
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
    Chat endpoint with streaming support
    
    Supports both authenticated users and guest sessions.
    Enforces plan limits before calling OpenAI.
    """
    # Determine if user or guest
    user_id = None
    guest_session = None
    questions_used = 0
    plan_type = PlanType.FREE
    
    if current_user:
        # Authenticated user
        user_id = current_user.id
        questions_used = current_user.questions_used
        plan_type = current_user.plan_type
    elif request.guest_session_id:
        # Guest session
        guest_session = get_or_create_guest_session(db, request.guest_session_id)
        questions_used = guest_session.questions_used
        plan_type = PlanType.FREE
    else:
        # No auth and no guest session - error
        from app.utils.errors import UnauthorizedException
        raise UnauthorizedException("Authentication or guest session ID required")
    
    # Check plan limit BEFORE calling OpenAI
    check_plan_limit(questions_used, plan_type)
    
    # Get or create conversation
    conversation = None
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        
        if not conversation:
            from app.utils.errors import NotFoundException
            raise NotFoundException("Conversation")
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            guest_session_id=guest_session.id if guest_session else None
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Get conversation history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Log user input
    logger.info(f"User Input (ConvID: {conversation.id}): {request.message}")
    
    # Increment usage count
    if current_user:
        increment_user_usage(db, current_user.id)
    else:
        increment_guest_usage(db, guest_session.id)
    
    # Process message with agent
    agent = MedicalChatAgent()
    
    # Convert attachments to dict format if present
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
        
        # Initialize request-level cost tracking
        request_total_cost = 0.0
        request_total_input_tokens = 0
        request_total_output_tokens = 0
        request_cost_breakdown = []
        
        try:
            async for chunk in agent.process_message(request.message, conversation_history, attachments_data):
                # Send chunk as Server-Sent Event
                if chunk["type"] == "content":
                    assistant_message_content += chunk["data"]
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                elif chunk["type"] == "metadata":
                    metadata.update(chunk["data"])
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                elif chunk["type"] == "done":
                    metadata.update(chunk["data"])
                    
                    # Extract cost data from agent metadata
                    request_total_cost = chunk["data"].get("total_cost", 0.0)
                    request_total_input_tokens = chunk["data"].get("total_input_tokens", 0)
                    request_total_output_tokens = chunk["data"].get("total_output_tokens", 0)
                    request_cost_breakdown = chunk["data"].get("cost_breakdown", [])
                    
                    # Save assistant message
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=assistant_message_content,
                        meta_data=metadata
                    )
                    
                    # Log assistant output
                    logger.info(f"Assistant Output (ConvID: {conversation.id}): {assistant_message_content[:200]}...") # Log first 200 chars to avoid clutter
                    db.add(assistant_message)
                    
                    # Update conversation title if first exchange
                    if not conversation.title:
                        # Use first 50 chars of user message as title
                        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
                    
                    db.commit()
                    db.refresh(assistant_message)
                    
                    # Log grand total cost for the entire request
                    if request_total_cost > 0:
                        from app.utils.cost_calculator import log_grand_total_cost
                        log_grand_total_cost(
                            total_cost=request_total_cost,
                            total_input_tokens=request_total_input_tokens,
                            total_output_tokens=request_total_output_tokens,
                            step_breakdown=request_cost_breakdown
                        )
                    
                    # Send final metadata with IDs
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
            # Send error to client
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
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
