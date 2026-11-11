from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from backend.app.models.task import Task
from backend.app.models.habit import Habit, HabitCompletion
from backend.app.models.focus import FocusSession
from backend.app.models.goal import Goal, Milestone
from backend.app.schemas.analytics import (
    AnalyticsSummary, CategoryBreakdown, ProductivityTrend,
    HabitAnalytics, FocusAnalytics, GoalAnalytics,
)


class AnalyticsService:
    """Computes real analytics from the user's actual activity data."""

    def _resolve_period(
        self, period: str, start_date: Optional[str], end_date: Optional[str]
    ) -> Tuple[datetime, datetime]:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if period == "today":
            return today_start, now
        elif period == "this_week":
            week_start = today_start - timedelta(days=today_start.weekday())
            return week_start, now
        elif period == "this_month":
            month_start = today_start.replace(day=1)
            return month_start, now
        elif period == "custom" and start_date and end_date:
            s = datetime.strptime(start_date, "%Y-%m-%d")
            e = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
            return s, e
        else:
            # Default to this week
            week_start = today_start - timedelta(days=today_start.weekday())
            return week_start, now

    # ------------------------------------------------------------------
    # Task analytics
    # ------------------------------------------------------------------
    def _task_metrics(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> dict:
        now = datetime.utcnow()

        # All tasks for this user
        all_q = db.query(Task).filter(Task.user_id == user_id)
        total = all_q.count()

        completed = all_q.filter(Task.is_completed == True).count()
        pending = all_q.filter(
            Task.is_completed == False, Task.status != "cancelled"
        ).count()
        overdue = all_q.filter(
            Task.is_completed == False,
            Task.due_date < now,
            Task.status != "cancelled",
        ).count()
        cancelled = all_q.filter(Task.status == "cancelled").count()
        in_progress = all_q.filter(Task.status == "in_progress").count()

        # Time estimates
        est_row = db.query(
            func.coalesce(func.sum(Task.estimated_minutes), 0)
        ).filter(Task.user_id == user_id).scalar()

        act_row = db.query(
            func.coalesce(func.sum(Task.actual_minutes), 0)
        ).filter(Task.user_id == user_id).scalar()

        # Completion rates by period
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        def _rate(since: datetime) -> float:
            created_since = all_q.filter(Task.created_at >= since).count()
            completed_since = all_q.filter(
                Task.is_completed == True, Task.completed_at >= since
            ).count()
            return round(completed_since / created_since * 100, 1) if created_since > 0 else 0.0

        daily_rate = _rate(today_start)
        weekly_rate = _rate(week_start)
        monthly_rate = _rate(month_start)

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "overdue_tasks": overdue,
            "cancelled_tasks": cancelled,
            "in_progress_tasks": in_progress,
            "total_estimated_minutes": int(est_row),
            "total_actual_minutes": int(act_row),
            "daily_completion_rate": daily_rate,
            "weekly_completion_rate": weekly_rate,
            "monthly_completion_rate": monthly_rate,
        }

    # ------------------------------------------------------------------
    # Category breakdown
    # ------------------------------------------------------------------
    def _category_breakdown(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> List[CategoryBreakdown]:
        cats = (
            db.query(
                Task.category,
                func.count(Task.id).label("total"),
                func.sum(
                    case((Task.is_completed == True, 1), else_=0)
                ).label("done"),
            )
            .filter(Task.user_id == user_id)
            .group_by(Task.category)
            .all()
        )

        results: List[CategoryBreakdown] = []
        for cat_name, total, done in cats:
            done = done or 0
            rate = round(done / total * 100, 1) if total > 0 else 0.0

            # Focus minutes linked via tasks in this category
            focus_min = (
                db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0))
                .join(Task, FocusSession.task_id == Task.id)
                .filter(
                    FocusSession.user_id == user_id,
                    Task.category == cat_name,
                    FocusSession.session_type == "focus",
                )
                .scalar()
            )

            results.append(
                CategoryBreakdown(
                    category=cat_name or "Uncategorized",
                    total_tasks=total,
                    completed_tasks=done,
                    completion_rate=rate,
                    total_focus_minutes=int(focus_min or 0),
                )
            )
        return results

    # ------------------------------------------------------------------
    # Habit analytics
    # ------------------------------------------------------------------
    def _habit_analytics(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> HabitAnalytics:
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        total = len(habits)
        active = sum(1 for h in habits if not h.is_archived)

        best_streak = max((h.best_streak for h in habits), default=0)
        current_best = max((h.streak_count for h in habits), default=0)

        # Completions in period
        p_start_str = p_start.strftime("%Y-%m-%d")
        p_end_str = p_end.strftime("%Y-%m-%d")
        completions = (
            db.query(HabitCompletion)
            .filter(
                HabitCompletion.user_id == user_id,
                HabitCompletion.completion_date >= p_start_str,
                HabitCompletion.completion_date <= p_end_str,
            )
            .count()
        )

        # Average completion rate: completions / (active_habits * days_in_period)
        days = max((p_end - p_start).days, 1)
        expected = active * days if active > 0 else 1
        avg_rate = round(min(completions / expected * 100, 100.0), 1)

        return HabitAnalytics(
            total_habits=total,
            active_habits=active,
            average_completion_rate=avg_rate,
            best_streak=best_streak,
            current_best_streak=current_best,
            completions_this_period=completions,
        )

    # ------------------------------------------------------------------
    # Focus analytics
    # ------------------------------------------------------------------
    def _focus_analytics(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> FocusAnalytics:
        base = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.session_type == "focus",
        )
        total_sessions = base.count()
        total_min = (
            db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0))
            .filter(
                FocusSession.user_id == user_id,
                FocusSession.session_type == "focus",
            )
            .scalar()
        )
        avg = round(int(total_min) / total_sessions, 1) if total_sessions > 0 else 0.0

        period_q = base.filter(FocusSession.started_at >= p_start, FocusSession.started_at <= p_end)
        period_sessions = period_q.count()
        period_min = (
            db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0))
            .filter(
                FocusSession.user_id == user_id,
                FocusSession.session_type == "focus",
                FocusSession.started_at >= p_start,
                FocusSession.started_at <= p_end,
            )
            .scalar()
        )

        return FocusAnalytics(
            total_sessions=total_sessions,
            total_focus_minutes=int(total_min),
            average_session_minutes=avg,
            sessions_this_period=period_sessions,
            focus_minutes_this_period=int(period_min),
        )

    # ------------------------------------------------------------------
    # Goal analytics
    # ------------------------------------------------------------------
    def _goal_analytics(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> GoalAnalytics:
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        total = len(goals)
        completed = sum(1 for g in goals if g.status == "completed")
        in_progress = sum(1 for g in goals if g.status == "in_progress")
        avg_progress = round(
            sum(g.progress_percentage for g in goals) / total, 1
        ) if total > 0 else 0.0

        total_milestones = db.query(Milestone).filter(Milestone.user_id == user_id).count()
        completed_milestones = db.query(Milestone).filter(
            Milestone.user_id == user_id, Milestone.is_completed == True
        ).count()

        return GoalAnalytics(
            total_goals=total,
            completed_goals=completed,
            in_progress_goals=in_progress,
            average_progress=avg_progress,
            total_milestones=total_milestones,
            completed_milestones=completed_milestones,
        )

    # ------------------------------------------------------------------
    # Productivity trends (day-by-day)
    # ------------------------------------------------------------------
    def _trends(
        self, db: Session, user_id: str, p_start: datetime, p_end: datetime
    ) -> List[ProductivityTrend]:
        trends: List[ProductivityTrend] = []
        current = p_start.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = p_end.replace(hour=23, minute=59, second=59)

        while current <= end_day:
            day_str = current.strftime("%Y-%m-%d")
            next_day = current + timedelta(days=1)

            # Tasks completed on this day
            completed = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.completed_at >= current,
                    Task.completed_at < next_day,
                )
                .count()
            )

            # Tasks created on this day
            created = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.created_at >= current,
                    Task.created_at < next_day,
                )
                .count()
            )

            # Focus minutes
            focus_min = (
                db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0))
                .filter(
                    FocusSession.user_id == user_id,
                    FocusSession.session_type == "focus",
                    FocusSession.started_at >= current,
                    FocusSession.started_at < next_day,
                )
                .scalar()
            )

            # Habits completed
            habits_done = (
                db.query(HabitCompletion)
                .filter(
                    HabitCompletion.user_id == user_id,
                    HabitCompletion.completion_date == day_str,
                )
                .count()
            )

            trends.append(
                ProductivityTrend(
                    date=day_str,
                    tasks_completed=completed,
                    tasks_created=created,
                    focus_minutes=int(focus_min),
                    habits_completed=habits_done,
                )
            )
            current = next_day

        return trends

    # ------------------------------------------------------------------
    # Main summary
    # ------------------------------------------------------------------
    def get_summary(
        self,
        db: Session,
        user_id: str,
        period: str = "this_week",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> AnalyticsSummary:
        p_start, p_end = self._resolve_period(period, start_date, end_date)

        task_m = self._task_metrics(db, user_id, p_start, p_end)

        # Total focus minutes across all time
        total_focus = (
            db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0))
            .filter(
                FocusSession.user_id == user_id,
                FocusSession.session_type == "focus",
            )
            .scalar()
        )

        return AnalyticsSummary(
            **task_m,
            total_focus_minutes=int(total_focus),
            habits=self._habit_analytics(db, user_id, p_start, p_end),
            focus=self._focus_analytics(db, user_id, p_start, p_end),
            goals=self._goal_analytics(db, user_id, p_start, p_end),
            category_breakdown=self._category_breakdown(db, user_id, p_start, p_end),
            trends=self._trends(db, user_id, p_start, p_end),
            period_start=p_start.strftime("%Y-%m-%d"),
            period_end=p_end.strftime("%Y-%m-%d"),
        )


analytics_service = AnalyticsService()
