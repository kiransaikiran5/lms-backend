from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.course import Course
from app.models.user import User
from app.schemas.payment import PaymentCreate
from fastapi import HTTPException, status, BackgroundTasks
import uuid
from app.core.email import send_payment_success_email
import logging
import asyncio

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def create_payment(db: Session, user_id: int, payment_data: PaymentCreate):
        # Verify course exists and price matches
        course = db.query(Course).filter(Course.id == payment_data.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if course.price != payment_data.amount:
            raise HTTPException(status_code=400, detail="Payment amount doesn't match course price")
        
        # Check if already paid
        existing_payment = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.course_id == payment_data.course_id,
            Payment.status == "completed"
        ).first()
        
        if existing_payment:
            raise HTTPException(status_code=400, detail="Payment already completed for this course")
        
        # Create payment record
        payment = Payment(
            user_id=user_id,
            course_id=payment_data.course_id,
            amount=payment_data.amount,
            status="pending",
            transaction_id=str(uuid.uuid4())
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        logger.info(f"💰 Payment created: {payment.transaction_id} for user {user_id}, amount ${payment.amount}")
        return payment
    
    @staticmethod
    def process_payment(db: Session, payment_id: int, background_tasks: BackgroundTasks = None):
        """Process a pending payment and send success email"""
        
        # Get payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Check if already processed
        if payment.status == "completed":
            raise HTTPException(status_code=400, detail="Payment already processed")
        
        if payment.status == "failed":
            raise HTTPException(status_code=400, detail="Payment already failed")
        
        # Get user and course
        user = db.query(User).filter(User.id == payment.user_id).first()
        course = db.query(Course).filter(Course.id == payment.course_id).first()
        
        if not user or not course:
            raise HTTPException(status_code=404, detail="User or Course not found")
        
        # Process payment (simulate)
        try:
            payment.status = "completed"
            db.commit()
            logger.info(f"✅ Payment processed: {payment.transaction_id} for {user.email}")
            
            # ========== SEND PAYMENT SUCCESS EMAIL ==========
            # This is the critical part - send email immediately
            try:
                if background_tasks:
                    # Use background tasks for async sending
                    background_tasks.add_task(
                        send_payment_success_email,
                        user.email,
                        user.full_name,
                        course.title,
                        payment.amount
                    )
                    logger.info(f"📧 Payment success email queued for {user.email}")
                else:
                    # Direct async call
                    asyncio.create_task(
                        send_payment_success_email(
                            user.email,
                            user.full_name,
                            course.title,
                            payment.amount
                        )
                    )
                    logger.info(f"📧 Payment success email triggered for {user.email}")
            except Exception as email_error:
                logger.error(f"❌ Failed to send payment email: {email_error}")
            
            return payment
            
        except Exception as e:
            payment.status = "failed"
            db.commit()
            logger.error(f"❌ Payment processing failed: {e}")
            raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")
    
    @staticmethod
    def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 10):
        payments = db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
        
        total = db.query(Payment).filter(Payment.user_id == user_id).count()
        
        return {"payments": payments, "total": total, "skip": skip, "limit": limit}