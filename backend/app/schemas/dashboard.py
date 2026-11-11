from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskSummaryItem(BaseModel):
    id: str
    title: str
    time: str
    category: str
    priority: str
    is_completed: bool

class DashboardSummaryResponse(BaseModel):
    greeting: str
    productivity_score: int
    productivity_status: str
    ai_tip: str
    completed_tasks_count: int
    pending_tasks_count: int
    focus_minutes_today: int
    active_habits_count: int
    today_tasks: List[TaskSummaryItem]
