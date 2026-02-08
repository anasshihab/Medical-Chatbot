"""Conversation API endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.models.user import User
from app.models.conversation import Conversation
from app.models.guest_session import GuestSession
from app.dependencies import get_current_user
from app.core.usage import get_or_create_guest_session
from app.utils.errors import NotFoundException

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationListResponse])
async def get_conversations(
    guest_session_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user or guest session"""
    
    # Determine if user or guest
    if current_user:
        # Authenticated user
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).all()
    
    elif guest_session_id:
        # Guest session
        guest_session = get_or_create_guest_session(db, guest_session_id)
        conversations = db.query(Conversation).filter(
            Conversation.guest_session_id == guest_session.id
        ).order_by(Conversation.updated_at.desc()).all()
    
    else:
        # No auth and no guest session - return empty list
        return []
    
    result = []
    for conv in conversations:
        # Get first user message for preview
        first_message = next((msg for msg in conv.messages if msg.role == "user"), None)
        preview = first_message.content[:100] if first_message else ""
        
        result.append(ConversationListResponse(
            id=conv.id,
            title=conv.title or "محادثة جديدة",
            summary=preview,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    guest_session_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific conversation with messages"""
    
    # Build query based on user type
    query = db.query(Conversation).filter(Conversation.id == conversation_id)
    
    if current_user:
        query = query.filter(Conversation.user_id == current_user.id)
    elif guest_session_id:
        guest_session = get_or_create_guest_session(db, guest_session_id)
        query = query.filter(Conversation.guest_session_id == guest_session.id)
    else:
        raise NotFoundException("Conversation")
    
    conversation = query.first()
    
    if not conversation:
        raise NotFoundException("Conversation")
    
    return ConversationResponse.model_validate(conversation)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    guest_session_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific conversation"""
    
    # Build query based on user type
    query = db.query(Conversation).filter(Conversation.id == conversation_id)
    
    if current_user:
        query = query.filter(Conversation.user_id == current_user.id)
    elif guest_session_id:
        from app.core.usage import get_or_create_guest_session
        guest_session = get_or_create_guest_session(db, guest_session_id)
        query = query.filter(Conversation.guest_session_id == guest_session.id)
    else:
        from app.utils.errors import UnauthorizedException
        raise UnauthorizedException("Authentication or guest session ID required")
    
    conversation = query.first()
    
    if not conversation:
        from app.utils.errors import NotFoundException
        raise NotFoundException("Conversation")
    
    db.delete(conversation)
    db.commit()
    
    return {"status": "success", "message": "Conversation deleted"}

