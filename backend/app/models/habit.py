from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from datetime import datetime
import uuid
from backend.app.database.session import Base

class Habit(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, default="Health")
    frequency = Column(String, default="daily")  # daily, weekly
    target_days_per_week = Column(Integer, default=7)
    streak_count = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String, ForeignKey("habits.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    completion_date = Column(String, index=True, nullable=False)  # "YYYY-MM-DD"
    created_at = Column(DateTime, default=datetime.utcnow)
