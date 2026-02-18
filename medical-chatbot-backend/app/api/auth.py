"""Authentication API endpoints"""
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import Token, AuthResponse, GuestAuthResponse
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.conversation import Conversation
from app.models.guest_session import GuestSession
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.config import settings
from app.dependencies import require_user
from app.utils.errors import AlreadyExistsException, UnauthorizedException
from app.utils.constants import WINDOW_HOURS
from jose import jwt

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    redirect_slashes=False,  # Prevent 307 redirects that break CORS preflight
)


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting reverse-proxy headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"




def create_guest_token(session_id: str) -> str:
    """
    Create a short-lived JWT for a guest session.
    Uses 'guest:<session_id>' as the 'sub' claim so it can never
    accidentally resolve to a real user_id integer.
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": f"guest:{session_id}",
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "guest",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


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


@router.post("/guest", response_model=GuestAuthResponse)
async def guest_login(request: Request, db: Session = Depends(get_db)):
    """
    Create (or reuse) a guest session and return a temporary JWT.

    IP Fingerprinting: Before creating a new session, we check if an active
    session already exists for this IP within the current 6-hour window.
    If so, we return the EXISTING session to prevent the "clear cookies" loophole.

    The client should:
    1. Store the returned `session_id` in localStorage as `med_id`.
    2. Store the returned `token.access_token` in localStorage as `med_token`.
    3. Pass `Authorization: Bearer <token>` on subsequent requests.
    """
    client_ip = _get_client_ip(request)
    window_start = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)

    # ── IP Fingerprint Check ─────────────────────────────────────────────────
    # Look for an existing active session from this IP within the current window
    existing_session = (
        db.query(GuestSession)
        .filter(
            GuestSession.client_ip == client_ip,
            GuestSession.created_at >= window_start,
        )
        .order_by(GuestSession.created_at.desc())
        .first()
    )

    if existing_session:
        # Reuse the existing session — do NOT grant fresh questions
        access_token = create_guest_token(existing_session.session_id)
        return GuestAuthResponse(
            token=Token(access_token=access_token),
            session_id=existing_session.session_id,
            question_count=existing_session.question_count,
        )

    # ── Create a fresh session ───────────────────────────────────────────────
    session_id = str(uuid.uuid4())
    guest_session = GuestSession(session_id=session_id, client_ip=client_ip)
    db.add(guest_session)
    db.commit()
    db.refresh(guest_session)

    access_token = create_guest_token(session_id)
    return GuestAuthResponse(
        token=Token(access_token=access_token),
        session_id=session_id,
        question_count=0,
    )


# Trailing-slash alias — some fetch clients append a trailing slash
@router.post("/guest/", response_model=GuestAuthResponse, include_in_schema=False)
async def guest_login_slash(request: Request, db: Session = Depends(get_db)):
    """Alias for /guest without trailing slash (prevents 404 / 307 redirect)."""
    return await guest_login(request, db)

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
