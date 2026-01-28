"""Authentication schemas"""
from pydantic import BaseModel
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
