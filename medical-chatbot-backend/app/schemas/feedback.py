"""Feedback schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.utils.constants import FeedbackType


class FeedbackRequest(BaseModel):
    """Feedback request schema"""
    message_id: int
    conversation_id: int
    feedback_type: FeedbackType
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response schema"""
    id: int
    feedback_type: FeedbackType
    reviewed: bool
    improved_response: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
