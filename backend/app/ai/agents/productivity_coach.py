"""
AI Productivity Coach — Evaluates actual user activity data to produce
personalized, actionable coaching insights and recommendations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter

from backend.app.models.task import Task
from backend.app.models.habit import Habit, HabitCompletion
from backend.app.models.focus import FocusSession
from backend.app.models.goal import Goal
from backend.app.schemas.ai import ProductivityInsight, ProductivityInsightsResponse


class ProductivityCoach:
    def analyze(self, db: Session, user_id: str) -> ProductivityInsightsResponse:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # 1. Task completions & peak hours
        completed_tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.is_completed == True,
                Task.completed_at != None,
            )
            .all()
        )

        hours = [t.completed_at.hour for t in completed_tasks if t.completed_at]
        hour_counts = Counter(hours)
        peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else None

        # 2. Overdue & pending tasks
        pending_tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.status != "cancelled",
            )
            .all()
        )
        overdue_count = sum(1 for t in pending_tasks if t.due_date and t.due_date < now)

        # 3. Focus sessions in the past 7 days
        recent_focus = (
            db.query(FocusSession)
            .filter(
                FocusSession.user_id == user_id,
                FocusSession.session_type == "focus",
                FocusSession.started_at >= seven_days_ago,
            )
            .all()
        )
        total_focus_minutes = sum(f.duration_minutes for f in recent_focus)

        # 4. Habits
        habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.is_archived == False).all()
        active_habits_count = len(habits)
        best_streak = max((h.streak_count for h in habits), default=0)

        # 5. Goals
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        avg_goal_progress = sum(g.progress_percentage for g in goals) / len(goals) if goals else 0.0

        # Generate personalized insights
        insights: List[ProductivityInsight] = []
        score_components = []

        # Peak productive hours insight
        if peak_hour is not None:
            time_str = f"{peak_hour % 12 or 12}:00 {'PM' if peak_hour >= 12 else 'AM'}"
            insights.append(
                ProductivityInsight(
                    category="timing",
                    title="Prime Focus Window Detected",
                    description=(
                        f"You complete most tasks around {time_str}. "
                        "Schedule your most demanding, high-priority tasks during this window."
                    ),
                    priority="info",
                )
            )
            score_components.append(85)
        else:
            insights.append(
                ProductivityInsight(
                    category="timing",
                    title="Establishing Energy Rhythm",
                    description="Complete a few more tasks to unlock your personalized peak focus hours.",
                    priority="info",
                )
            )
            score_components.append(70)

        # Overdue handling insight
        if overdue_count > 0:
            insights.append(
                ProductivityInsight(
                    category="tasks",
                    title=f"{overdue_count} Overdue Tasks Need Attention",
                    description="Tasks postponed frequently lead to mental friction. Use the AI Rescheduler to realign dates.",
                    priority="warning",
                )
            )
            score_components.append(max(40, 80 - overdue_count * 5))
        else:
            insights.append(
                ProductivityInsight(
                    category="tasks",
                    title="Zero Overdue Backlog",
                    description="Great job keeping your task list clean and on-schedule!",
                    priority="info",
                )
            )
            score_components.append(95)

        # Focus session insight
        if total_focus_minutes >= 120:
            insights.append(
                ProductivityInsight(
                    category="focus",
                    title=f"Strong Focus Momentum ({total_focus_minutes} min logged)",
                    description="Your deep work stamina is solid. Remember to take short breaks to sustain cognitive quality.",
                    priority="info",
                )
            )
            score_components.append(90)
        elif total_focus_minutes > 0:
            insights.append(
                ProductivityInsight(
                    category="focus",
                    title=f"Building Focus Habit ({total_focus_minutes} min)",
                    description="Try doing at least two 25-minute Pomodoro sessions daily for deep work.",
                    priority="suggestion",
                )
            )
            score_components.append(75)
        else:
            insights.append(
                ProductivityInsight(
                    category="focus",
                    title="Activate Deep Work Timer",
                    description="No Pomodoro sessions logged in the last 7 days. Start with a single 25-minute block.",
                    priority="suggestion",
                )
            )
            score_components.append(60)

        # Habit streak insight
        if best_streak >= 5:
            insights.append(
                ProductivityInsight(
                    category="habits",
                    title=f"Consistent Habit Momentum ({best_streak}-day streak)",
                    description="Habit streaks reflect strong discipline. Maintain the chain!",
                    priority="info",
                )
            )
            score_components.append(90)
        elif active_habits_count > 0:
            insights.append(
                ProductivityInsight(
                    category="habits",
                    title="Habit Consistency in Progress",
                    description="Check in your daily habits every morning or evening to build an unbroken chain.",
                    priority="suggestion",
                )
            )
            score_components.append(70)

        # Goal progress insight
        if goals:
            insights.append(
                ProductivityInsight(
                    category="goals",
                    title=f"Active Goals Tracked ({round(avg_goal_progress)}% average)",
                    description="Keep knocking down individual milestones to drive long-term objective progress.",
                    priority="info",
                )
            )

        overall_score = round(sum(score_components) / len(score_components), 1) if score_components else 75.0

        if overall_score >= 85:
            summary = "High performance across tasks, focus, and consistency. Maintain this pace."
        elif overall_score >= 70:
            summary = "Balanced productivity foundation with actionable opportunities in focus sessions and overdue management."
        else:
            summary = "Let's reset and build steady rhythm by tackling overdue items and scheduling a 25-minute focus block."

        return ProductivityInsightsResponse(
            insights=insights,
            overall_score=overall_score,
            summary=summary,
        )


productivity_coach = ProductivityCoach()
