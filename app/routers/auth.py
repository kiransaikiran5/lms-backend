from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login_user(db, login_data.email, login_data.password)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(db, refresh_data.refresh_token)