from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List

from backend.app.models.task import Task
from backend.app.models.habit import Habit, HabitCompletion
from backend.app.models.focus import FocusSession
from backend.app.schemas.dashboard import DashboardSummaryResponse, TaskSummaryItem
from backend.app.ai.providers.mock_provider import MockAIProvider


class DashboardService:
    def __init__(self):
        self.ai_provider = MockAIProvider()

    async def get_dashboard_summary(
        self, db: Optional[Session] = None, user_id: str = "guest"
    ) -> DashboardSummaryResponse:
        # If no DB provided or user is guest, return clean baseline
        if not db or not user_id or user_id == "guest":
            return DashboardSummaryResponse(
                greeting="Welcome to PlanWise AI",
                productivity_score=0,
                productivity_status="Ready to Start",
                ai_tip="Create your first task or goal to begin tracking your progress.",
                today_tasks=0,
                completed_today=0,
                pending_tasks=0,
                overdue_tasks=0,
                current_streak=0,
                focus_minutes_today=0,
                completed_tasks_count=0,
                pending_tasks_count=0,
                active_habits_count=0,
                upcoming_tasks=[],
                today_schedule=[],
                today_tasks_list=[],
            )

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 1. Tasks
        all_user_tasks = db.query(Task).filter(Task.user_id == user_id)

        # Pending tasks (overall)
        pending_count = all_user_tasks.filter(
            Task.is_completed == False,
            Task.status != "cancelled"
        ).count()

        # Overdue tasks
        overdue_count = all_user_tasks.filter(
            Task.is_completed == False,
            Task.due_date < now,
            Task.status != "cancelled"
        ).count()

        # Tasks due today or created today
        today_tasks_query = all_user_tasks.filter(
            or_(
                and_(Task.due_date >= today_start, Task.due_date < today_end),
                and_(Task.created_at >= today_start, Task.created_at < today_end)
            )
        )
        today_tasks_total = today_tasks_query.count()

        # Completed today
        completed_today_count = all_user_tasks.filter(
            Task.is_completed == True,
            Task.completed_at >= today_start,
            Task.completed_at < today_end
        ).count()

        # If today_tasks_total is 0 but user has completed tasks today, align today_tasks_total
        if completed_today_count > today_tasks_total:
            today_tasks_total = completed_today_count

        # 2. Focus Minutes Today
        focus_minutes = db.query(
            func.coalesce(func.sum(FocusSession.duration_minutes), 0)
        ).filter(
            FocusSession.user_id == user_id,
            FocusSession.started_at >= today_start,
            FocusSession.started_at < today_end,
            FocusSession.completed == True
        ).scalar() or 0

        # 3. Active Habits & Current Streak
        user_habits = db.query(Habit).filter(
            Habit.user_id == user_id,
            Habit.is_archived == False
        ).all()
        active_habits_count = len(user_habits)
        max_streak = max([h.streak_count for h in user_habits], default=0)

        # 4. Productivity Score Calculation (Real Activity Only)
        if today_tasks_total == 0 and completed_today_count == 0 and focus_minutes == 0:
            productivity_score = 0
            productivity_status = "No Activity Today"
        else:
            task_ratio = (completed_today_count / today_tasks_total) if today_tasks_total > 0 else 0.0
            task_score = task_ratio * 60
            focus_score = min(30.0, (focus_minutes / 60.0) * 30.0)
            streak_score = min(10.0, float(max_streak))
            productivity_score = min(100, int(round(task_score + focus_score + streak_score)))

            if productivity_score >= 80:
                productivity_status = "High Performance"
            elif productivity_score >= 50:
                productivity_status = "Steady Progress"
            else:
                productivity_status = "Building Momentum"

        # 5. Upcoming Tasks & Schedule
        upcoming_tasks_records = all_user_tasks.filter(
            Task.is_completed == False,
            Task.due_date >= now,
            Task.status != "cancelled"
        ).order_by(Task.due_date.asc()).limit(5).all()

        upcoming_list = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "category": t.category,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "is_completed": t.is_completed,
            }
            for t in upcoming_tasks_records
        ]

        today_scheduled_records = today_tasks_query.order_by(
            Task.due_date.asc(), Task.priority.desc()
        ).limit(10).all()

        today_schedule_list = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "category": t.category,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "is_completed": t.is_completed,
            }
            for t in today_scheduled_records
        ]

        summary_tasks = [
            TaskSummaryItem(
                id=t.id,
                title=t.title,
                time=(t.due_date.strftime("%I:%M %p") if t.due_date else "Today"),
                category=t.category or "General",
                priority=t.priority or "medium",
                is_completed=t.is_completed,
            )
            for t in today_scheduled_records
        ]

        # Greeting logic
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # AI Tip based on actual metrics
        tip = await self.ai_provider.get_productivity_tip({"score": productivity_score})

        return DashboardSummaryResponse(
            today_tasks=today_tasks_total,
            completed_today=completed_today_count,
            pending_tasks=pending_count,
            overdue_tasks=overdue_count,
            current_streak=max_streak,
            focus_minutes_today=int(focus_minutes),
            productivity_score=productivity_score,
            productivity_status=productivity_status,
            upcoming_tasks=upcoming_list,
            today_schedule=today_schedule_list,
            greeting=greeting,
            ai_tip=tip,
            completed_tasks_count=completed_today_count,
            pending_tasks_count=pending_count,
            active_habits_count=active_habits_count,
            today_tasks_list=summary_tasks,
        )


dashboard_service = DashboardService()
