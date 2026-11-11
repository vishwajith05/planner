"""
AI service — coordinates the scheduling engine, NL parser, and analytics
to serve AI endpoints.  All data-modifying actions produce *suggestions*
that the user must confirm.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from backend.app.models.task import Task
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.habit import Habit, HabitCompletion
from backend.app.models.focus import FocusSession
from backend.app.models.goal import Goal, Milestone

from backend.app.ai.scheduling.daily_scheduler import build_daily_schedule
from backend.app.ai.scheduling.weekly_planner import build_weekly_plan
from backend.app.ai.scheduling.rescheduler import find_missed_tasks, suggest_reschedule
from backend.app.ai.providers.mock_provider import MockAIProvider


_mock = MockAIProvider()


class AIService:
    """Stateless service bridging DB queries with deterministic AI logic."""

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _tasks_as_dicts(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        return [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "category": t.category,
                "estimated_minutes": t.estimated_minutes or 30,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "is_completed": t.is_completed,
                "status": t.status,
            }
            for t in tasks
        ]

    def _events_as_dicts(
        self, events: List[CalendarEvent]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "title": e.title,
                "start": e.start_time.isoformat(),
                "end": e.end_time.isoformat(),
                "is_fixed": e.is_fixed,
            }
            for e in events
        ]

    def _pending_tasks(self, db: Session, user_id: str) -> List[Task]:
        return (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.status != "cancelled",
            )
            .order_by(Task.due_date.asc().nulls_last())
            .all()
        )

    # ------------------------------------------------------------------ #
    # NL Quick-Add
    # ------------------------------------------------------------------ #
    async def parse_quick_add(self, prompt: str) -> Dict[str, Any]:
        return await _mock.parse_quick_add(prompt)

    # ------------------------------------------------------------------ #
    # Daily Schedule
    # ------------------------------------------------------------------ #
    def daily_schedule(
        self,
        db: Session,
        user_id: str,
        date: str = "",
        day_start_hour: int = 8,
        day_end_hour: int = 22,
    ) -> Dict[str, Any]:
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        # Pending tasks
        tasks = self._tasks_as_dicts(self._pending_tasks(db, user_id))

        # Fixed commitments for the day
        day_dt = datetime.strptime(date, "%Y-%m-%d")
        next_day = day_dt + timedelta(days=1)
        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_id == user_id,
                CalendarEvent.is_fixed == True,
                CalendarEvent.start_time >= day_dt,
                CalendarEvent.start_time < next_day,
            )
            .all()
        )
        fixed = self._events_as_dicts(events)

        return build_daily_schedule(
            tasks=tasks,
            fixed_commitments=fixed,
            day_date=date,
            day_start_hour=day_start_hour,
            day_end_hour=day_end_hour,
        )

    # ------------------------------------------------------------------ #
    # Weekly Plan
    # ------------------------------------------------------------------ #
    def weekly_plan(
        self,
        db: Session,
        user_id: str,
        week_start: str = "",
        day_start_hour: int = 8,
        day_end_hour: int = 22,
        rest_days: Optional[List[int]] = None,
        max_minutes_per_day: int = 480,
    ) -> Dict[str, Any]:
        tasks = self._tasks_as_dicts(self._pending_tasks(db, user_id))

        # All fixed events for the week
        if not week_start:
            today = datetime.utcnow()
            ws_dt = today - timedelta(days=today.weekday())
        else:
            ws_dt = datetime.strptime(week_start, "%Y-%m-%d")
        we_dt = ws_dt + timedelta(days=7)

        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_id == user_id,
                CalendarEvent.is_fixed == True,
                CalendarEvent.start_time >= ws_dt,
                CalendarEvent.start_time < we_dt,
            )
            .all()
        )
        fixed = self._events_as_dicts(events)

        return build_weekly_plan(
            tasks=tasks,
            fixed_commitments=fixed,
            week_start=ws_dt.strftime("%Y-%m-%d"),
            day_start_hour=day_start_hour,
            day_end_hour=day_end_hour,
            rest_days=rest_days or [],
            max_minutes_per_day=max_minutes_per_day,
        )

    # ------------------------------------------------------------------ #
    # Reschedule
    # ------------------------------------------------------------------ #
    def reschedule(
        self,
        db: Session,
        user_id: str,
        days_ahead: int = 3,
        day_start_hour: int = 8,
        day_end_hour: int = 22,
    ) -> Dict[str, Any]:
        all_tasks = self._tasks_as_dicts(self._pending_tasks(db, user_id))
        missed = find_missed_tasks(all_tasks)

        if not missed:
            return {
                "suggestions": [],
                "could_not_reschedule": [],
                "days_searched": days_ahead,
                "message": "No overdue tasks found. You're on track!",
            }

        # Get existing scheduled events as blocked slots
        now = datetime.utcnow()
        end_dt = now + timedelta(days=days_ahead)
        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.user_id == user_id,
                CalendarEvent.start_time >= now,
                CalendarEvent.start_time < end_dt,
            )
            .all()
        )
        fixed = self._events_as_dicts(events)

        return suggest_reschedule(
            missed_tasks=missed,
            fixed_commitments=fixed,
            existing_scheduled=[],
            day_start_hour=day_start_hour,
            day_end_hour=day_end_hour,
            days_ahead=days_ahead,
        )

    # ------------------------------------------------------------------ #
    # Workload Analysis
    # ------------------------------------------------------------------ #
    def workload_analysis(
        self, db: Session, user_id: str
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        pending = self._pending_tasks(db, user_id)
        total_min = sum(t.estimated_minutes or 30 for t in pending)
        overdue = sum(1 for t in pending if t.due_date and t.due_date < now)

        # Today load
        today_tasks = [
            t for t in pending
            if t.due_date and t.due_date >= today and t.due_date < tomorrow
        ]
        today_min = sum(t.estimated_minutes or 30 for t in today_tasks)

        # Tomorrow load
        day_after = tomorrow + timedelta(days=1)
        tmrw_tasks = [
            t for t in pending
            if t.due_date and t.due_date >= tomorrow and t.due_date < day_after
        ]
        tmrw_min = sum(t.estimated_minutes or 30 for t in tmrw_tasks)

        # Next 7 days by day
        day_loads: Dict[str, int] = {}
        for i in range(7):
            d = today + timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            d_next = d + timedelta(days=1)
            d_min = sum(
                t.estimated_minutes or 30
                for t in pending
                if t.due_date and t.due_date >= d and t.due_date < d_next
            )
            day_loads[d_str] = d_min

        busiest = max(day_loads, key=day_loads.get) if day_loads else today.strftime("%Y-%m-%d")
        lightest = min(day_loads, key=day_loads.get) if day_loads else today.strftime("%Y-%m-%d")

        is_overloaded = today_min > 480  # more than 8 hours

        recommendations: List[str] = []
        if overdue > 0:
            recommendations.append(
                f"You have {overdue} overdue task(s). Consider rescheduling them."
            )
        if is_overloaded:
            recommendations.append(
                f"Today's workload ({today_min} min) exceeds 8 hours. "
                "Move lower-priority tasks to lighter days."
            )
        if total_min > 2400:
            recommendations.append(
                f"Total pending workload is {total_min} min ({round(total_min/60, 1)} hrs). "
                "Consider prioritizing or delegating tasks."
            )
        if not recommendations:
            recommendations.append("Workload looks balanced. Keep it up!")

        return {
            "total_pending_minutes": total_min,
            "overdue_count": overdue,
            "today_load_minutes": today_min,
            "tomorrow_load_minutes": tmrw_min,
            "busiest_day": busiest,
            "lightest_day": lightest,
            "is_overloaded": is_overloaded,
            "recommendations": recommendations,
        }


ai_service = AIService()
