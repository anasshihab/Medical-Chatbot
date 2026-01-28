"""FastAPI dependencies"""
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.guest_session import GuestSession
from app.core.auth import decode_access_token, extract_token_from_header
from app.core.usage import get_or_create_guest_session
from app.utils.errors import UnauthorizedException


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token
    Returns None if no token provided (for optional auth)
    Raises UnauthorizedException if token is invalid
    """
    if not authorization:
        return None
    
    token = extract_token_from_header(authorization)
    if not token:
        raise UnauthorizedException("Invalid authorization header")
    
    user_id = decode_access_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise UnauthorizedException("User not found")
    
    return user


def require_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """
    Require authenticated user (for protected endpoints)
    Raises UnauthorizedException if not authenticated
    """
    token = extract_token_from_header(authorization)
    if not token:
        raise UnauthorizedException("Authentication required")
    
    user_id = decode_access_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise UnauthorizedException("User not found")
    
    return user


def get_guest_session(
    guest_session_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[GuestSession]:
    """Get or create guest session if guest_session_id provided"""
    if not guest_session_id:
        return None
    
    return get_or_create_guest_session(db, guest_session_id)
