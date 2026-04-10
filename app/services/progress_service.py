from sqlalchemy.orm import Session
from app.models.progress import Progress
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.schemas.progress import MarkLessonComplete
from fastapi import HTTPException, status
from datetime import datetime

class ProgressService:
    @staticmethod
    def mark_lesson_complete(db: Session, user_id: int, lesson_id: int):
        # Check if lesson exists
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Check if user is enrolled in the course
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == lesson.course_id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=403, detail="Must be enrolled in the course to complete lessons")
        
        # Update or create progress
        progress = db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.lesson_id == lesson_id
        ).first()
        
        if not progress:
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                completed=1,
                completed_at=datetime.utcnow()
            )
            db.add(progress)
        else:
            progress.completed = 1
            progress.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Lesson marked as completed", "lesson_id": lesson_id}
    
    @staticmethod
    def get_course_progress(db: Session, user_id: int, course_id: int):
        # Check enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        # Get all lessons in the course
        lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
        total_lessons = len(lessons)
        
        if total_lessons == 0:
            return {
                "course_id": course_id,
                "total_lessons": 0,
                "completed_lessons": 0,
                "progress_percentage": 0,
                "lessons_progress": []
            }
        
        # Get completed lessons
        completed = []
        lessons_progress = []
        
        for lesson in lessons:
            progress = db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.lesson_id == lesson.id,
                Progress.completed == 1
            ).first()
            
            is_completed = progress is not None
            if is_completed:
                completed.append(lesson)
            
            lessons_progress.append({
                "lesson_id": lesson.id,
                "completed": is_completed,
                "completed_at": progress.completed_at if progress else None
            })
        
        completed_count = len(completed)
        progress_percentage = (completed_count / total_lessons) * 100
        
        return {
            "course_id": course_id,
            "total_lessons": total_lessons,
            "completed_lessons": completed_count,
            "progress_percentage": round(progress_percentage, 2),
            "lessons_progress": lessons_progress
        }