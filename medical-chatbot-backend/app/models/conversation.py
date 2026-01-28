"""Conversation model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Conversation(Base):
    """Conversation model for chat sessions"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Can belong to either a user or guest session
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_session_id = Column(Integer, ForeignKey("guest_sessions.id"), nullable=True)
    
    # Conversation metadata
    title = Column(String, nullable=True)  # Auto-generated from first message
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    guest_session = relationship("GuestSession", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    feedbacks = relationship("Feedback", back_populates="conversation", cascade="all, delete-orphan")
