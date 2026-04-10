from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MarkLessonComplete(BaseModel):
    lesson_id: int

class ProgressResponse(BaseModel):
    lesson_id: int
    completed: bool
    completed_at: Optional[datetime]

class CourseProgressResponse(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    lessons_progress: list[ProgressResponse]