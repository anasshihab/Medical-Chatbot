"""Chat schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str
    conversation_id: Optional[int] = None
    guest_session_id: Optional[str] = None  # For guest mode


class ChatResponse(BaseModel):
    """Chat response schema (for non-streaming)"""
    response: str
    conversation_id: int
    message_id: int
    metadata: Dict[str, Any] = {}


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    type: str  # "content", "metadata", "done"
    data: Any
