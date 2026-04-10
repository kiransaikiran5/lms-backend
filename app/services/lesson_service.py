from sqlalchemy.orm import Session
from app.models.lesson import Lesson
from app.models.course import Course
from app.schemas.lesson import LessonCreate, LessonUpdate
from fastapi import HTTPException, status

class LessonService:
    @staticmethod
    def create_lesson(db: Session, lesson_data: LessonCreate, course_id: int, user_id: int, user_role: str):
        # Check course exists and permission
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if user_role != "admin" and course.instructor_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to add lessons to this course")
        
        db_lesson = Lesson(course_id=course_id, **lesson_data.dict())
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    
    @staticmethod
    def get_course_lessons(db: Session, course_id: int, skip: int = 0, limit: int = 50):
        lessons = db.query(Lesson).filter(
            Lesson.course_id == course_id
        ).order_by(Lesson.order).offset(skip).limit(limit).all()
        
        total = db.query(Lesson).filter(Lesson.course_id == course_id).count()
        
        return {"lessons": lessons, "total": total}
    
    @staticmethod
    def update_lesson(db: Session, lesson_id: int, lesson_data: LessonUpdate, user_id: int, user_role: str):
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        course = db.query(Course).filter(Course.id == lesson.course_id).first()
        if user_role != "admin" and course.instructor_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this lesson")
        
        for field, value in lesson_data.dict(exclude_unset=True).items():
            setattr(lesson, field, value)
        
        db.commit()
        db.refresh(lesson)
        return lesson