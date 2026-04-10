from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (UniqueConstraint('user_id', 'lesson_id', name='unique_progress'),)