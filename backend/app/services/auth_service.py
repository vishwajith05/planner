from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, UserProfileUpdate
from backend.app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def register_user(self, db: Session, user_in: UserCreate) -> User:
        existing = db.query(User).filter(User.email == user_in.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists"
            )
        
        user = User(
            email=user_in.email.lower(),
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            timezone=user_in.timezone or "UTC"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, login_data: UserLogin) -> dict:
        user = db.query(User).filter(User.email == login_data.email.lower()).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated"
            )
            
        token = create_access_token(subject=user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }

    def update_profile(self, db: Session, user: User, profile_in: UserProfileUpdate) -> User:
        if profile_in.full_name is not None:
            user.full_name = profile_in.full_name
        if profile_in.timezone is not None:
            user.timezone = profile_in.timezone
        if profile_in.bio is not None:
            user.bio = profile_in.bio
            
        db.commit()
        db.refresh(user)
        return user

auth_service = AuthService()
