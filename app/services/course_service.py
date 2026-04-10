from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.schemas.course import CourseCreate, CourseUpdate
from fastapi import HTTPException, status

class CourseService:
    @staticmethod
    def create_course(db: Session, course_data: CourseCreate, instructor_id: int):
        db_course = Course(
            title=course_data.title,
            description=course_data.description,
            price=course_data.price,
            instructor_id=instructor_id
        )
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    
    @staticmethod
    def get_courses(db: Session, skip: int = 0, limit: int = 10, 
                   sort_by: str = "created_at", order: str = "desc",
                   min_price: float = None, max_price: float = None,
                   instructor_id: int = None):
        query = db.query(Course)
        
        # Filters
        if min_price is not None:
            query = query.filter(Course.price >= min_price)
        if max_price is not None:
            query = query.filter(Course.price <= max_price)
        if instructor_id is not None:
            query = query.filter(Course.instructor_id == instructor_id)
        
        # Sorting
        if order == "desc":
            query = query.order_by(desc(getattr(Course, sort_by)))
        else:
            query = query.order_by(asc(getattr(Course, sort_by)))
        
        # Pagination
        courses = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return {"courses": courses, "total": total}
    
    @staticmethod
    def get_course_detail(db: Session, course_id: int):
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        total_lessons = db.query(Lesson).filter(Lesson.course_id == course_id).count()
        total_enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
        
        # Add computed fields to course object
        course.total_lessons = total_lessons
        course.total_enrollments = total_enrollments
        
        return course
    
    @staticmethod
    def get_courses_by_instructor(db: Session, instructor_id: int):
        courses = db.query(Course).filter(Course.instructor_id == instructor_id).all()
        return {"courses": courses, "total": len(courses)}
    
    @staticmethod
    def update_course(db: Session, course_id: int, course_data: CourseUpdate, user_id: int, user_role: str):
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check permission
        if user_role != "admin" and course.instructor_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this course")
        
        for field, value in course_data.dict(exclude_unset=True).items():
            setattr(course, field, value)
        
        db.commit()
        db.refresh(course)
        return course
    
    @staticmethod
    def delete_course(db: Session, course_id: int, user_id: int, user_role: str):
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check permission
        if user_role != "admin" and course.instructor_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this course")
        
        db.delete(course)
        db.commit()
        return {"message": "Course deleted successfully"}