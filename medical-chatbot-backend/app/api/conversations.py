"""Conversation API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.models.user import User
from app.models.conversation import Conversation
from app.dependencies import require_user
from app.utils.errors import NotFoundException

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationListResponse])
async def get_conversations(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        result.append(ConversationListResponse(
            id=conv.id,
            title=conv.title,
            summary=conv.summary,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get specific conversation with messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise NotFoundException("Conversation")
    
    return ConversationResponse.model_validate(conversation)
