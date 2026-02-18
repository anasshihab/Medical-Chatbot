"""Guest session model"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class GuestSession(Base):
    """Guest session model for unauthenticated users"""
    __tablename__ = "guest_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    client_ip = Column(String, nullable=True, index=True)  # IP fingerprint for loophole prevention
    questions_used = Column(Integer, default=0, nullable=False)

    # 6-hour rolling window usage tracking
    question_count = Column(Integer, default=0, nullable=False)
    last_reset_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="guest_session", cascade="all, delete-orphan")
