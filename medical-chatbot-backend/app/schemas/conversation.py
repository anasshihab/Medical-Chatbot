"""Conversation schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageResponse(BaseModel):
    """Message response schema"""
    id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: int
    title: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Conversation list response schema"""
    id: int
    title: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    model_config = ConfigDict(from_attributes=True)
