from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Friendship ──────────────────────────────────────────────────────────────

class FriendRequest(BaseModel):
    addressee_email: str = Field(..., description="Email of the user to send friend request to")


class FriendRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    requester_id: str
    addressee_id: str
    status: str
    created_at: datetime


class FriendProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    friendship_id: str
    friendship_status: str


# ── Shared Challenges ───────────────────────────────────────────────────────

class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = "General"
    duration_days: int = 30
    daily_target: Optional[str] = None
    weekly_target: Optional[str] = None
    start_date: Optional[datetime] = None
    friend_ids: Optional[List[str]] = []  # User IDs to invite


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    creator_id: str
    title: str
    description: Optional[str]
    category: str
    duration_days: str
    daily_target: Optional[str]
    weekly_target: Optional[str]
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    participants: Optional[List[dict]] = []
    created_at: datetime


class ChallengeProgressUpdate(BaseModel):
    progress_percent: int = Field(..., ge=0, le=100)
    days_completed: Optional[int] = None


# ── Encouragement Messages ──────────────────────────────────────────────────

class EncouragementCreate(BaseModel):
    recipient_id: str
    message: str = Field(..., min_length=1, max_length=500)
    challenge_id: Optional[str] = None


class EncouragementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sender_id: str
    recipient_id: str
    challenge_id: Optional[str]
    message: str
    is_read: bool
    created_at: datetime


# ── Focus Together ──────────────────────────────────────────────────────────

class FocusSessionCreate(BaseModel):
    title: str = "Focus Together Session"
    duration_minutes: int = 25


class FocusSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    host_id: str
    title: str
    duration_minutes: str
    status: str
    session_code: str
    participants: Optional[List[dict]] = []
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
