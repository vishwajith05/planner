from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

EMAIL_PATTERN = r"^[\w\.\+-]+@[\w\.-]+\.[a-zA-Z]{2,}$"

class UserBase(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN, description="Valid email address")
    full_name: Optional[str] = None
    timezone: Optional[str] = "UTC"
    bio: Optional[str] = None

class UserCreate(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN, description="Valid email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = None
    timezone: Optional[str] = "UTC"

class UserLogin(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
