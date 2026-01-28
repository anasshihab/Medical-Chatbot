"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import Token, AuthResponse
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.conversation import Conversation
from app.models.guest_session import GuestSession
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.dependencies import require_user
from app.utils.errors import AlreadyExistsException, UnauthorizedException

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    If guest_session_id provided, merge guest conversations to user account
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise AlreadyExistsException("User with this email")
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Merge guest data if guest_session_id provided
    if user_data.guest_session_id:
        guest_session = db.query(GuestSession).filter(
            GuestSession.session_id == user_data.guest_session_id
        ).first()
        
        if guest_session:
            # Transfer conversations to user
            db.query(Conversation).filter(
                Conversation.guest_session_id == guest_session.id
            ).update({
                "user_id": new_user.id,
                "guest_session_id": None
            })
            
            # Transfer usage count
            new_user.questions_used = guest_session.questions_used
            
            # Delete guest session
            db.delete(guest_session)
            db.commit()
            db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(new_user.id)
    
    return AuthResponse(
        token=Token(access_token=access_token),
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")
    
    # Create access token
    access_token = create_access_token(user.id)
    
    return AuthResponse(
        token=Token(access_token=access_token),
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)
    
    In a stateless JWT system, logout is handled client-side by removing the token.
    This endpoint exists for consistency and can be extended with token blacklisting if needed.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(require_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)
