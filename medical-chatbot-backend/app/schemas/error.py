"""Error schemas"""
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.utils.constants import ErrorCode


class ErrorDetail(BaseModel):
    """Error detail schema"""
    code: ErrorCode
    message: str
    details: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Unified error response schema"""
    error: ErrorDetail
