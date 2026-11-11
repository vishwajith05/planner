from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from datetime import datetime
import uuid
from backend.app.database.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, urgent
    status = Column(String, default="not_started")  # not_started, in_progress, completed, cancelled
    category = Column(String, default="Personal")
    tags = Column(String, default="")  # comma-separated tags
    estimated_minutes = Column(Integer, default=30)
    start_time = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
