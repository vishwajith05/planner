from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime


class CategoryBreakdown(BaseModel):
    category: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    total_focus_minutes: int

    model_config = ConfigDict(from_attributes=True)


class ProductivityTrend(BaseModel):
    date: str  # YYYY-MM-DD
    tasks_completed: int
    tasks_created: int
    focus_minutes: int
    habits_completed: int

    model_config = ConfigDict(from_attributes=True)


class HabitAnalytics(BaseModel):
    total_habits: int
    active_habits: int
    average_completion_rate: float
    best_streak: int
    current_best_streak: int
    completions_this_period: int

    model_config = ConfigDict(from_attributes=True)


class FocusAnalytics(BaseModel):
    total_sessions: int
    total_focus_minutes: int
    average_session_minutes: float
    sessions_this_period: int
    focus_minutes_this_period: int

    model_config = ConfigDict(from_attributes=True)


class GoalAnalytics(BaseModel):
    total_goals: int
    completed_goals: int
    in_progress_goals: int
    average_progress: float
    total_milestones: int
    completed_milestones: int

    model_config = ConfigDict(from_attributes=True)


class DailyCompletionItem(BaseModel):
    date: str
    count: int


class AnalyticsSummary(BaseModel):
    # Period
    period: str = "this_week"
    period_start: str
    period_end: str

    # Task metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    cancelled_tasks: int = 0
    in_progress_tasks: int = 0

    # Completion rates
    completion_rate: float = 0.0
    daily_completion_rate: float = 0.0
    weekly_completion_rate: float = 0.0
    monthly_completion_rate: float = 0.0

    # Time tracking
    total_estimated_minutes: int = 0
    total_actual_minutes: int = 0
    total_focus_minutes: int = 0

    # Frontend UI analytics fields
    productivity_score: int = 0
    habit_streak_average: float = 0.0
    peak_hour: Optional[int] = None
    daily_completions: List[DailyCompletionItem] = []

    # Sub-analytics
    habits: HabitAnalytics
    focus: FocusAnalytics
    goals: GoalAnalytics

    # Category breakdown (List of CategoryBreakdown for tests & charts)
    category_breakdown: List[CategoryBreakdown] = []

    # Trends (day-by-day)
    trends: List[ProductivityTrend] = []

    model_config = ConfigDict(from_attributes=True)


class AnalyticsQuery(BaseModel):
    """Query parameters for analytics filtering."""
    period: str = "this_week"  # today, this_week, this_month, custom
    start_date: Optional[str] = None  # YYYY-MM-DD for custom
    end_date: Optional[str] = None    # YYYY-MM-DD for custom
