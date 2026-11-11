from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_fixed: bool = False
    task_id: Optional[str] = None
    category: Optional[str] = "General"

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventResponse(CalendarEventBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TimeConflict(BaseModel):
    existing_event_id: str
    existing_event_title: str
    start_time: datetime
    end_time: datetime
    is_fixed: bool
    conflict_reason: str

class ConflictCheckRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    ignore_event_id: Optional[str] = None

class ConflictCheckResponse(BaseModel):
    has_conflict: bool
    conflicts: List[TimeConflict]
