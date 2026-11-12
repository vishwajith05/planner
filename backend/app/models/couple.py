from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from datetime import datetime
import uuid
from backend.app.database.session import Base


class CoupleRelationship(Base):
    __tablename__ = "couple_relationships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_a_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    partner_b_id = Column(String, ForeignKey("users.id"), index=True, nullable=False, default="")
    invite_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")  # pending, active, ended
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)


class SharedGoal(Base):
    __tablename__ = "shared_goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String, ForeignKey("couple_relationships.id"), index=True, nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="General")
    target_date = Column(DateTime, nullable=True)
    partner_a_progress = Column(Integer, default=0)  # 0-100
    partner_b_progress = Column(Integer, default=0)  # 0-100
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SharedHabit(Base):
    __tablename__ = "shared_habits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String, ForeignKey("couple_relationships.id"), index=True, nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String, default="daily")
    partner_a_streak = Column(Integer, default=0)
    partner_b_streak = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SharedHabitCompletion(Base):
    __tablename__ = "shared_habit_completions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String, ForeignKey("shared_habits.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    completion_date = Column(String, index=True, nullable=False)  # "YYYY-MM-DD"
    created_at = Column(DateTime, default=datetime.utcnow)


class CoupleCheckIn(Base):
    __tablename__ = "couple_check_ins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String, ForeignKey("couple_relationships.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    mood = Column(String, default="good")  # great, good, okay, low
    gratitude = Column(Text, nullable=True)
    win_of_day = Column(Text, nullable=True)
    support_needed = Column(Text, nullable=True)
    check_in_date = Column(String, index=True, nullable=False)  # "YYYY-MM-DD"
    created_at = Column(DateTime, default=datetime.utcnow)


class CoupleChallenge(Base):
    __tablename__ = "couple_challenges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String, ForeignKey("couple_relationships.id"), index=True, nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, default=30)
    partner_a_progress = Column(Integer, default=0)
    partner_b_progress = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
