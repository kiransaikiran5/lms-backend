from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_instructor, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Only admin
):
    """Get all users (Admin only)"""
    return UserService.get_all_users(db, skip, limit, role)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    return UserService.get_user(db, user_id, current_user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user"""
    return UserService.update_user(db, user_id, user_data, current_user)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete user (Admin only)"""
    return UserService.delete_user(db, user_id)

@router.get("/instructors/courses")
def get_instructor_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Get courses for current instructor"""
    from app.services.course_service import CourseService
    return CourseService.get_courses_by_instructor(db, current_user.id)