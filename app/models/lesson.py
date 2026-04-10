from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    video_url = Column(String(500))
    order = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())