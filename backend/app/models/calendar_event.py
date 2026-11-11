from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from datetime import datetime
import uuid
from backend.app.database.session import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    is_fixed = Column(Boolean, default=False)  # Fixed commitment like classes/meetings
    category = Column(String, default="General")
    created_at = Column(DateTime, default=datetime.utcnow)
