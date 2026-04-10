from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService
from app.models.user import User

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/", response_model=EnrollmentResponse)
def enroll_course(
    enrollment_data: EnrollmentCreate,
    background_tasks: BackgroundTasks,  # Add this
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return EnrollmentService.enroll_student(db, current_user.id, enrollment_data.course_id, background_tasks)

@router.get("/my-courses")
def get_my_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return EnrollmentService.get_user_enrollments(db, current_user.id, skip, limit)

@router.delete("/{course_id}")
def unenroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return EnrollmentService.unenroll_student(db, current_user.id, course_id)