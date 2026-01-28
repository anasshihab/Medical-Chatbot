"""Profile management API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserResponse, UserProfileUpdate
from app.models.user import User
from app.dependencies import require_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=UserResponse)
async def get_profile(current_user: User = Depends(require_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.put("", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    
    if profile_data.age is not None:
        current_user.age = profile_data.age
    
    if profile_data.gender is not None:
        current_user.gender = profile_data.gender
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.delete("")
async def delete_profile(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
