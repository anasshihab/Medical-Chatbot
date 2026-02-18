"""Authentication schemas"""
from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserResponse


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int


class AuthResponse(BaseModel):
    """Authentication response with token and user data"""
    token: Token
    user: UserResponse


class GuestAuthResponse(BaseModel):
    """Guest authentication response — token + session ID (no full user object)"""
    token: Token
    session_id: str
    question_count: int = 0  # Reused session usage
    is_guest: bool = True
