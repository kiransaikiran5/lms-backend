from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    order: int
    duration_minutes: Optional[int] = 0

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    order: Optional[int] = None

class LessonResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    order: int
    duration_minutes: Optional[int] = 0
    created_at: datetime
    
    class Config:
        from_attributes = True