from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from typing import Optional, List

class UserService:
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10, role: Optional[str] = None):
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        
        users = query.offset(skip).limit(limit).all()
        return users
    
    @staticmethod
    def get_user(db: Session, user_id: int, current_user: User):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Users can only view their own profile unless admin
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this user")
        
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate, current_user: User):
        # Check permission
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this user")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}