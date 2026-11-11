from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class FocusSessionCreate(BaseModel):
    task_id: Optional[str] = None
    duration_minutes: int = Field(default=25, ge=1, le=180)
    session_type: str = Field(default="focus", pattern="^(focus|short_break|long_break)$")
    completed: bool = True
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class FocusSessionResponse(BaseModel):
    id: str
    user_id: str
    task_id: Optional[str] = None
    duration_minutes: int
    session_type: str
    completed: bool
    notes: Optional[str] = None
    started_at: datetime
    ended_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FocusStatsResponse(BaseModel):
    total_focus_minutes_today: int
    total_sessions_today: int
    total_focus_minutes_this_week: int
    total_sessions_this_week: int
