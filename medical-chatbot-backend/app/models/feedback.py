"""Feedback model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.utils.constants import FeedbackType


class Feedback(Base):
    """Feedback model for message ratings and improvements"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    
    # Feedback data
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    comment = Column(Text, nullable=True)
    
    # For negative feedback - improved response
    reviewed = Column(Boolean, default=False, nullable=False)
    improved_response = Column(Text, nullable=True)
    improved_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    conversation = relationship("Conversation", back_populates="feedbacks")
