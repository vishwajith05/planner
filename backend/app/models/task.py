from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from datetime import datetime
import uuid
from backend.app.database.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Priorities: low, medium, high, urgent
    priority = Column(String, default="medium", index=True)
    
    # Statuses: not_started, in_progress, completed, cancelled
    status = Column(String, default="not_started", index=True)
    
    # Categorization
    category = Column(String, default="Personal", index=True)
    tags = Column(String, default="")  # comma-separated or json string
    list_name = Column(String, default="Inbox", index=True)
    
    # Timing & Estimation
    estimated_minutes = Column(Integer, default=30)
    actual_minutes = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True, index=True)
    reminder_time = Column(DateTime, nullable=True)
    
    # Recurrence: none, daily, weekly, monthly, yearly, custom
    recurrence = Column(String, default="none")
    
    # Subtasks & Checklists (stored as JSON arrays)
    # Subtask format: [{"id": "...", "title": "...", "is_completed": false}]
    subtasks = Column(JSON, default=list)
    
    is_completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
