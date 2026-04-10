from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.payment import Payment
from app.models.user import User
from fastapi import HTTPException, status, BackgroundTasks
from app.core.email import send_enrollment_email
import logging

logger = logging.getLogger(__name__)

class EnrollmentService:
    @staticmethod
    def enroll_student(db: Session, user_id: int, course_id: int, background_tasks: BackgroundTasks = None):
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already enrolled
        existing = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Check if payment is completed (for paid courses)
        if course.price > 0:
            payment = db.query(Payment).filter(
                Payment.user_id == user_id,
                Payment.course_id == course_id,
                Payment.status == "completed"
            ).first()
            
            if not payment:
                raise HTTPException(status_code=400, detail="Payment required for this course")
        
        # Create enrollment
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        
        # SEND ENROLLMENT CONFIRMATION EMAIL
        user = db.query(User).filter(User.id == user_id).first()
        
        if user and course:
            try:
                if background_tasks:
                    background_tasks.add_task(
                        send_enrollment_email,
                        user.email,
                        user.full_name,
                        course.title
                    )
                    logger.info(f"✅ Enrollment email queued for {user.email}")
                else:
                    import asyncio
                    asyncio.create_task(send_enrollment_email(
                        user.email, user.full_name, course.title
                    ))
                    logger.info(f"✅ Enrollment email triggered for {user.email}")
            except Exception as e:
                logger.error(f"❌ Failed to send enrollment email: {e}")
        
        return enrollment
    
    @staticmethod
    def get_user_enrollments(db: Session, user_id: int, skip: int = 0, limit: int = 10):
        enrollments = db.query(Enrollment).filter(
            Enrollment.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        total = db.query(Enrollment).filter(Enrollment.user_id == user_id).count()
        
        return {"enrollments": enrollments, "total": total}
    
    @staticmethod
    def unenroll_student(db: Session, user_id: int, course_id: int):
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        db.delete(enrollment)
        db.commit()
        
        return {"message": "Successfully unenrolled from course"}