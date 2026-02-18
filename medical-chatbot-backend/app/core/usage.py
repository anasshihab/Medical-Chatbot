"""Usage tracking utilities with 6-hour rolling window reset logic"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.guest_session import GuestSession
from app.utils.constants import WINDOW_HOURS


def _now_utc() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def _make_aware(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware (assume UTC if naive)."""
    if dt is None:
        return _now_utc()
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _window_expired(last_reset_at: datetime) -> bool:
    """Return True if the 6-hour window has elapsed since last_reset_at."""
    aware_reset = _make_aware(last_reset_at)
    return (_now_utc() - aware_reset) >= timedelta(hours=WINDOW_HOURS)


def next_reset_time(last_reset_at: datetime) -> datetime:
    """Return the UTC datetime when the current window expires."""
    aware_reset = _make_aware(last_reset_at)
    return aware_reset + timedelta(hours=WINDOW_HOURS)


# ── User helpers ───────────────────────────────────────────────────────────────

def check_and_reset_user_window(db: Session, user: User) -> None:
    """
    If the 6-hour window has elapsed, reset question_count and update
    last_reset_at.  Commits the change immediately.
    """
    if _window_expired(user.last_reset_at):
        user.question_count = 0
        user.last_reset_at = _now_utc()
        db.commit()
        db.refresh(user)


def increment_user_usage(db: Session, user_id: int) -> None:
    """Increment both the rolling-window counter and the all-time counter."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.question_count += 1
        user.questions_used += 1
        db.commit()


# ── Guest helpers ──────────────────────────────────────────────────────────────

def check_and_reset_guest_window(db: Session, session: GuestSession) -> None:
    """
    If the 6-hour window has elapsed, reset question_count and update
    last_reset_at for a guest session.
    """
    if _window_expired(session.last_reset_at):
        session.question_count = 0
        session.last_reset_at = _now_utc()
        db.commit()
        db.refresh(session)


def increment_guest_usage(db: Session, guest_session_id: int) -> None:
    """Increment both the rolling-window counter and the all-time counter."""
    session = db.query(GuestSession).filter(GuestSession.id == guest_session_id).first()
    if session:
        session.question_count += 1
        session.questions_used += 1
        db.commit()


def get_or_create_guest_session(db: Session, session_id: str) -> GuestSession:
    """Get or create guest session by session ID."""
    guest_session = db.query(GuestSession).filter(
        GuestSession.session_id == session_id
    ).first()

    if not guest_session:
        guest_session = GuestSession(
            session_id=session_id,
            last_reset_at=_now_utc()
        )
        db.add(guest_session)
        db.commit()
        db.refresh(guest_session)

    return guest_session
