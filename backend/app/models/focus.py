from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from datetime import datetime
import uuid
from backend.app.database.session import Base

class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    duration_minutes = Column(Integer, default=25)
    session_type = Column(String, default="focus")  # focus, short_break, long_break
    completed = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, default=datetime.utcnow)
