from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/initiate", response_model=PaymentResponse)
def initiate_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Initiate a payment for a course"""
    return PaymentService.create_payment(db, current_user.id, payment_data)

@router.post("/{payment_id}/process", response_model=PaymentResponse)
def process_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Process a payment - This will send a Payment Success Email"""
    payment = PaymentService.process_payment(db, payment_id, background_tasks)
    
    # Verify payment belongs to current user
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to process this payment")
    
    return payment

@router.get("/my-payments")
def get_my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get payment history for current user"""
    return PaymentService.get_user_payments(db, current_user.id, skip, limit)