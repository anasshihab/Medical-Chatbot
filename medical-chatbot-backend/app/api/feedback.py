"""Feedback API endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.models.user import User
from app.models.feedback import Feedback
from app.models.message import Message
from app.models.conversation import Conversation
from app.dependencies import get_current_user
from app.agent.agent import MedicalChatAgent
from app.utils.constants import FeedbackType
from app.utils.errors import NotFoundException
from typing import Optional

router = APIRouter(prefix="/api", tags=["Feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_data: FeedbackRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a message
    
    - Thumbs up: Store only
    - Thumbs down: Trigger review agent and generate improved response
    """
    # Verify message exists
    message = db.query(Message).filter(
        Message.id == feedback_data.message_id
    ).first()
    
    if not message:
        raise NotFoundException("Message")
    
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == feedback_data.conversation_id
    ).first()
    
    if not conversation:
        raise NotFoundException("Conversation")
    
    # Create feedback
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        conversation_id=feedback_data.conversation_id,
        message_id=feedback_data.message_id,
        feedback_type=feedback_data.feedback_type,
        comment=feedback_data.comment
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # If thumbs down, trigger review agent
    if feedback_data.feedback_type == FeedbackType.THUMBS_DOWN:
        await process_negative_feedback(feedback, message, conversation, db)
    
    return FeedbackResponse.model_validate(feedback)


async def process_negative_feedback(
    feedback: Feedback,
    original_message: Message,
    conversation: Conversation,
    db: Session
):
    """
    Process negative feedback with review agent
    
    1. Re-run search if needed
    2. Generate improved answer
    3. Store as improved response
    """
    try:
        # Get conversation history up to the original message
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.created_at <= original_message.created_at
        ).order_by(Message.created_at).all()
        
        # Get the user message that prompted the original response
        user_message = None
        for i, msg in enumerate(messages):
            if msg.id == original_message.id and i > 0:
                user_message = messages[i - 1]
                break
        
        if not user_message:
            return
        
        # Build conversation history
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[:-2]  # Exclude the last user-assistant pair
        ]
        
        # Re-run agent with review prompt
        agent = MedicalChatAgent()
        improved_content = ""
        metadata = {}
        
        # Add review context to the message
        review_message = f"{user_message.content}\n\n[REVIEW MODE: User was not satisfied with the previous response. Please provide a more helpful, detailed, and accurate answer.]"
        
        async for chunk in agent.process_message(review_message, conversation_history):
            if chunk["type"] == "content":
                improved_content += chunk["data"]
            elif chunk["type"] == "metadata":
                metadata.update(chunk["data"])
        
        # Save improved response
        improved_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=improved_content,
            metadata={**metadata, "is_improved": True, "original_message_id": original_message.id}
        )
        db.add(improved_message)
        
        # Update feedback
        feedback.reviewed = True
        feedback.improved_response = improved_content
        feedback.improved_message_id = improved_message.id
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing negative feedback: {str(e)}")
        # Don't fail the feedback submission if review fails
        pass
