"""Chat schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class FileAttachment(BaseModel):
    """File attachment schema"""
    file_data: str  # Base64 encoded file data
    file_type: str  # MIME type (e.g., image/jpeg, audio/wav, application/pdf)
    file_name: str  # Original filename
    file_size: int  # Size in bytes


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str
    conversation_id: Optional[int] = None
    guest_session_id: Optional[str] = None  # For guest mode
    attachments: Optional[List[FileAttachment]] = None  # File attachments


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
