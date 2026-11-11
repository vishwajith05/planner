from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

class SubtaskItem(BaseModel):
    id: str
    title: str
    is_completed: bool = False

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    status: str = Field(default="not_started", pattern="^(not_started|in_progress|completed|cancelled)$")
    category: str = Field(default="Personal")
    tags: Optional[str] = ""
    list_name: str = Field(default="Inbox")
    estimated_minutes: int = Field(default=30, ge=1)
    actual_minutes: int = Field(default=0, ge=0)
    start_time: Optional[datetime] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence: str = Field(default="none", pattern="^(none|daily|weekly|monthly|yearly|custom)$")
    subtasks: List[SubtaskItem] = Field(default_factory=list)
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed|cancelled)$")
    category: Optional[str] = None
    tags: Optional[str] = None
    list_name: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=1)
    actual_minutes: Optional[int] = Field(None, ge=0)
    start_time: Optional[datetime] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence: Optional[str] = Field(None, pattern="^(none|daily|weekly|monthly|yearly|custom)$")
    subtasks: Optional[List[SubtaskItem]] = None
    is_completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: str
    user_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id: str
    name: str
    color: str
    icon: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = "#6366F1"
    icon: Optional[str] = "folder"
