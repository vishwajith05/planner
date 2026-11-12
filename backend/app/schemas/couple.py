from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Couple Relationship ─────────────────────────────────────────────────────

class CoupleInviteCreate(BaseModel):
    pass  # Creates an invite code for the current user


class CoupleInviteAccept(BaseModel):
    invite_code: str = Field(..., description="Unique invite code from partner")


class CoupleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    partner_a_id: str
    partner_b_id: str
    invite_code: str
    status: str
    partner_a: Optional[dict] = None
    partner_b: Optional[dict] = None
    created_at: datetime
    activated_at: Optional[datetime]


# ── Shared Goals ────────────────────────────────────────────────────────────

class SharedGoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = "General"
    target_date: Optional[datetime] = None


class SharedGoalProgressUpdate(BaseModel):
    progress: int = Field(..., ge=0, le=100)


class SharedGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    couple_id: str
    creator_id: str
    title: str
    description: Optional[str]
    category: str
    target_date: Optional[datetime]
    partner_a_progress: int
    partner_b_progress: int
    combined_progress: float
    is_completed: bool
    created_at: datetime


# ── Shared Habits ───────────────────────────────────────────────────────────

class SharedHabitCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    frequency: str = "daily"


class SharedHabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    couple_id: str
    title: str
    description: Optional[str]
    frequency: str
    partner_a_streak: int
    partner_b_streak: int
    is_active: bool
    today_partner_a_done: Optional[bool] = False
    today_partner_b_done: Optional[bool] = False
    created_at: datetime


# ── Check-ins ───────────────────────────────────────────────────────────────

class CheckInCreate(BaseModel):
    mood: str = "good"  # great, good, okay, low
    gratitude: Optional[str] = None
    win_of_day: Optional[str] = None
    support_needed: Optional[str] = None


class CheckInResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    couple_id: str
    user_id: str
    mood: str
    gratitude: Optional[str]
    win_of_day: Optional[str]
    support_needed: Optional[str]
    check_in_date: str
    created_at: datetime


# ── Couple Challenges ───────────────────────────────────────────────────────

class CoupleChallengeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration_days: int = 30
    start_date: Optional[datetime] = None


class CoupleChallengeProgressUpdate(BaseModel):
    progress: int = Field(..., ge=0, le=100)


class CoupleChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    couple_id: str
    title: str
    description: Optional[str]
    duration_days: int
    partner_a_progress: int
    partner_b_progress: int
    combined_progress: float
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
