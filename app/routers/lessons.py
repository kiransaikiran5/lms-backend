from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_instructor, get_current_user, get_current_admin
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.services.lesson_service import LessonService
from app.models.user import User
from app.models.enrollment import Enrollment
from app.models.course import Course

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.post("/courses/{course_id}", response_model=LessonResponse)
def create_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Create a new lesson (Instructor or Admin only)"""
    return LessonService.create_lesson(db, lesson_data, course_id, current_user.id, current_user.role)

@router.get("/courses/{course_id}")
def get_course_lessons(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Changed: Any authenticated user
):
    """Get all lessons for a course (Student, Instructor, or Admin)"""
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check access permissions
    has_access = False
    
    # Admin can access any course
    if current_user.role == "admin":
        has_access = True
    
    # Instructor can access their own courses
    elif current_user.role == "instructor" and course.instructor_id == current_user.id:
        has_access = True
    
    # Student can access only if enrolled
    elif current_user.role == "student":
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
        
        if enrollment:
            has_access = True
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail="You don't have access to view these lessons. Please enroll in the course first."
        )
    
    return LessonService.get_course_lessons(db, course_id, skip, limit)

@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Update a lesson (Instructor or Admin only)"""
    return LessonService.update_lesson(db, lesson_id, lesson_data, current_user.id, current_user.role)

@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Delete a lesson (Instructor or Admin only)"""
    return LessonService.delete_lesson(db, lesson_id, current_user.id, current_user.role)