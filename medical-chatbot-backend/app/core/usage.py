"""Usage tracking utilities"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.guest_session import GuestSession


def increment_user_usage(db: Session, user_id: int) -> None:
    """Increment question count for user"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.questions_used += 1
        db.commit()


def increment_guest_usage(db: Session, guest_session_id: int) -> None:
    """Increment question count for guest session"""
    session = db.query(GuestSession).filter(GuestSession.id == guest_session_id).first()
    if session:
        session.questions_used += 1
        db.commit()


def get_or_create_guest_session(db: Session, session_id: str) -> GuestSession:
    """Get or create guest session by session ID"""
    guest_session = db.query(GuestSession).filter(
        GuestSession.session_id == session_id
    ).first()
    
    if not guest_session:
        guest_session = GuestSession(session_id=session_id)
        db.add(guest_session)
        db.commit()
        db.refresh(guest_session)
    
    return guest_session
