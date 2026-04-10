from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_instructor, get_current_admin, get_current_user
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse
from app.services.course_service import CourseService
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/", response_model=CourseResponse)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    return CourseService.create_course(db, course_data, current_user.id)

@router.get("/")
def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|price|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    instructor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return CourseService.get_courses(db, skip, limit, sort_by, order, min_price, max_price, instructor_id)

@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    return CourseService.get_course_detail(db, course_id)

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    return CourseService.update_course(db, course_id, course_data, current_user.id, current_user.role)

@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    return CourseService.delete_course(db, course_id, current_user.id, current_user.role)