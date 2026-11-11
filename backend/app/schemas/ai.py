from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


# ---------- Quick-Add NL Parsing ----------
class QuickAddRequest(BaseModel):
    prompt: str


class QuickAddResponse(BaseModel):
    title: str
    category: str
    priority: str
    estimated_minutes: int
    suggested_due_date: Optional[str] = None
    start_time: Optional[str] = None
    recurrence: str = "none"
    confidence: float
    provider: str


# ---------- Daily Schedule ----------
class DailyScheduleRequest(BaseModel):
    date: str = ""  # YYYY-MM-DD, defaults to today
    day_start_hour: int = 8
    day_end_hour: int = 22
    include_breaks: bool = True


class ScheduledSlot(BaseModel):
    task_id: Optional[str] = None
    title: str
    priority: str = "medium"
    category: str = ""
    start: str
    end: str
    duration_minutes: int
    energy_level: int = 5


class DailyScheduleResponse(BaseModel):
    date: str
    scheduled: List[ScheduledSlot]
    unscheduled: List[Dict[str, Any]]
    warnings: List[str]
    total_work_minutes: int
    break_minutes: int
    slots_used: int
    available_hours: int


# ---------- Weekly Plan ----------
class WeeklyPlanRequest(BaseModel):
    week_start: str = ""  # YYYY-MM-DD of Monday
    day_start_hour: int = 8
    day_end_hour: int = 22
    rest_days: List[int] = []  # 0=Mon, 6=Sun
    max_minutes_per_day: int = 480


class WeeklyPlanResponse(BaseModel):
    week_start: str
    day_plans: List[Dict[str, Any]]
    unscheduled: List[Dict[str, Any]]
    warnings: List[str]
    total_work_minutes: int


# ---------- Reschedule ----------
class RescheduleRequest(BaseModel):
    days_ahead: int = 3
    day_start_hour: int = 8
    day_end_hour: int = 22


class RescheduleSuggestion(BaseModel):
    task_id: Optional[str] = None
    title: str
    priority: str = "medium"
    original_due: Optional[str] = None
    suggested_start: str
    suggested_end: str
    day: str
    duration_minutes: int


class RescheduleResponse(BaseModel):
    suggestions: List[RescheduleSuggestion]
    could_not_reschedule: List[Dict[str, Any]]
    days_searched: int


# ---------- Workload Analysis ----------
class WorkloadAnalysisResponse(BaseModel):
    total_pending_minutes: int
    overdue_count: int
    today_load_minutes: int
    tomorrow_load_minutes: int
    busiest_day: str
    lightest_day: str
    is_overloaded: bool
    recommendations: List[str]


# ---------- AI Chat ----------
class ChatMessage(BaseModel):
    role: str = "user"  # user | assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    actions: List[Dict[str, Any]] = []  # suggested actions the user can confirm
    data: Optional[Dict[str, Any]] = None


# ---------- Goal Breakdown ----------
class GoalBreakdownRequest(BaseModel):
    goal_title: str
    goal_description: str = ""
    target_date: Optional[str] = None
    category: str = "Personal"


class MilestoneSuggestion(BaseModel):
    title: str
    description: str = ""
    estimated_days: int = 7
    order: int = 0


class GoalBreakdownResponse(BaseModel):
    goal_title: str
    milestones: List[MilestoneSuggestion]
    estimated_total_days: int
    recommendations: List[str]


# ---------- Productivity Insights ----------
class ProductivityInsight(BaseModel):
    category: str  # e.g. "timing", "habits", "focus", "tasks"
    title: str
    description: str
    priority: str = "info"  # info, suggestion, warning


class ProductivityInsightsResponse(BaseModel):
    insights: List[ProductivityInsight]
    overall_score: float
    summary: str
