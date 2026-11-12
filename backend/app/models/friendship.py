from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from datetime import datetime
import uuid
import enum
from backend.app.database.session import Base


class FriendshipStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    blocked = "blocked"


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    addressee_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String, default="pending", index=True)  # pending, accepted, rejected, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SharedChallenge(Base):
    __tablename__ = "shared_challenges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="General")
    duration_days = Column(String, default="30")
    daily_target = Column(Text, nullable=True)   # JSON: list of daily tasks
    weekly_target = Column(Text, nullable=True)  # JSON: list of weekly goals
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey("shared_challenges.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    progress_percent = Column(String, default="0")  # 0-100
    days_completed = Column(String, default="0")
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_check_in = Column(DateTime, nullable=True)


class EncouragementMessage(Base):
    __tablename__ = "encouragement_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    challenge_id = Column(String, ForeignKey("shared_challenges.id"), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FocusTogetherSession(Base):
    __tablename__ = "focus_together_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    host_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, default="Focus Session")
    duration_minutes = Column(String, default="25")
    status = Column(String, default="waiting")  # waiting, active, completed
    session_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)


class FocusSessionParticipant(Base):
    __tablename__ = "focus_session_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("focus_together_sessions.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
