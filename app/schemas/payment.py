from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentCreate(BaseModel):
    course_id: int
    amount: float

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    amount: float
    status: str
    transaction_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True