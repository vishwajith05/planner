from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    category: Optional[str] = "Health"
    frequency: str = Field(default="daily", pattern="^(daily|weekly)$")
    target_days_per_week: int = Field(default=7, ge=1, le=7)

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly)$")
    target_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    is_archived: Optional[bool] = None

class HabitResponse(HabitBase):
    id: str
    user_id: str
    streak_count: int
    best_streak: int
    is_archived: bool
    is_completed_today: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HabitToggleResponse(BaseModel):
    habit_id: str
    date: str
    is_completed: bool
    current_streak: int
    best_streak: int

class HabitStatsResponse(BaseModel):
    total_active_habits: int
    completed_today_count: int
    daily_completion_rate: float
    longest_active_streak: int
