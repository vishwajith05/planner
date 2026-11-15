from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Friendship ──────────────────────────────────────────────────────────────

class FriendRequest(BaseModel):
    addressee_email: Optional[str] = Field(None, description="Email of the user to send friend request to")
    friend_id: Optional[str] = Field(None, description="User ID of the friend to connect with")
    addressee_id: Optional[str] = Field(None, description="User ID of the addressee")


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
    recipient_id: Optional[str] = None
    friend_id: Optional[str] = None
    message: Optional[str] = None
    content: Optional[str] = None
    challenge_id: Optional[str] = None

class DirectMessageCreate(BaseModel):
    recipient_id: Optional[str] = None
    friend_id: Optional[str] = None
    content: Optional[str] = None
    message: Optional[str] = None
    challenge_id: Optional[str] = None

class DirectMessageResponse(BaseModel):
    id: str
    sender_id: str
    sender_name: str
    recipient_id: str
    recipient_name: Optional[str] = None
    content: str
    is_read: bool
    created_at: str

class ConversationSummary(BaseModel):
    friend_id: str
    friend_name: str
    friend_email: str
    last_message: Optional[str] = None
    last_message_at: Optional[str] = None
    last_message_sender_id: Optional[str] = None
    unread_count: int = 0


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
