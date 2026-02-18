"""User model"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.utils.constants import PlanType


class User(Base):
    """User model for registered users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Plan information
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    questions_used = Column(Integer, default=0, nullable=False)

    # 6-hour rolling window usage tracking
    question_count = Column(Integer, default=0, nullable=False)
    last_reset_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Profile information
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
