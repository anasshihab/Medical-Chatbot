"""User schemas"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.utils.constants import PlanType


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str
    guest_session_id: Optional[str] = None  # For merging guest data


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Schema for user profile data"""
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class UserProfileUpdate(UserProfile):
    """Schema for updating user profile"""
    pass


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    plan_type: PlanType
    questions_used: int
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
