from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.schemas.progress import MarkLessonComplete, CourseProgressResponse
from app.services.progress_service import ProgressService
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/complete")
def mark_lesson_complete(
    complete_data: MarkLessonComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return ProgressService.mark_lesson_complete(db, current_user.id, complete_data.lesson_id)

@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return ProgressService.get_course_progress(db, current_user.id, course_id)