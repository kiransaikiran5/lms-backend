from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CourseBase(BaseModel):
    title: str
    description: str
    price: float

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_published: Optional[bool] = None

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    instructor_id: int
    is_published: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CourseDetailResponse(CourseResponse):
    total_lessons: int
    total_enrollments: int