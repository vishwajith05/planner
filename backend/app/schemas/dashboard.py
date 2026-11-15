from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class TaskSummaryItem(BaseModel):
    id: str
    title: str
    time: str
    category: str
    priority: str
    is_completed: bool

class DashboardSummaryResponse(BaseModel):
    # Standard DashboardStats fields for Frontend
    today_tasks: int = 0
    completed_today: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    current_streak: int = 0
    focus_minutes_today: int = 0
    productivity_score: int = 0
    upcoming_tasks: List[Any] = []
    today_schedule: List[Any] = []

    # Compatibility fields
    greeting: str = "Welcome back"
    productivity_status: str = "Ready"
    ai_tip: str = "Stay focused on your highest priority task today."
    completed_tasks_count: int = 0
    pending_tasks_count: int = 0
    active_habits_count: int = 0
    today_tasks_list: List[TaskSummaryItem] = []
