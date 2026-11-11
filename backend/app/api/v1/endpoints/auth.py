from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserProfileUpdate
from backend.app.services.auth_service import auth_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db=db, user_in=user_in)

@router.post("/login", response_model=TokenResponse, summary="Log in and retrieve JWT bearer access token")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_user(db=db, login_data=login_data)

@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse, summary="Update current user profile")
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.update_profile(db=db, user=current_user, profile_in=profile_in)
