"""
Conversational AI Agent — Natural language productivity assistant with Agentic Tool Architecture.
Executes lightweight tool-calling (get_user_tasks, create_task, get_user_goals,
get_productivity_stats, get_calendar_events) using strict user data isolation.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

from backend.app.models.task import Task
from backend.app.models.goal import Goal, Milestone
from backend.app.models.calendar_event import CalendarEvent
from backend.app.services.ai_service import ai_service
from backend.app.ai.agents.productivity_coach import productivity_coach
from backend.app.schemas.ai import ChatResponse, GoalBreakdownResponse, MilestoneSuggestion


class ChatAgent:
    """Agentic productivity assistant with integrated database tools."""

    # ── AGENTIC TOOLS ───────────────────────────────────────────────────────

    def tool_get_user_tasks(
        self, db: Session, user_id: str, is_completed: Optional[bool] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        query = db.query(Task).filter(Task.user_id == user_id)
        if is_completed is not None:
            query = query.filter(Task.is_completed == is_completed)
        tasks = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).limit(limit).all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "category": t.category,
                "is_completed": t.is_completed,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in tasks
        ]

    def tool_create_task(
        self,
        db: Session,
        user_id: str,
        title: str,
        priority: str = "medium",
        category: str = "Personal",
        due_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            priority=priority,
            category=category,
            due_date=due_date,
            status="not_started",
            is_completed=False,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return {
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "category": task.category,
            "is_completed": task.is_completed,
        }

    def tool_get_user_goals(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        return [
            {
                "id": g.id,
                "title": g.title,
                "category": g.category,
                "progress_percentage": g.progress_percentage,
                "status": g.status,
                "milestones_count": len(g.milestones) if g.milestones else 0,
            }
            for g in goals
        ]

    def tool_get_calendar_events(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        events = db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= today_start,
        ).order_by(CalendarEvent.start_time.asc()).limit(10).all()
        return [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "category": e.category,
            }
            for e in events
        ]

    # ── AGENT REASONING & DISPATCH ──────────────────────────────────────────

    def handle_message(self, db: Session, user_id: str, message: str) -> ChatResponse:
        low = message.strip().lower()

        # 1. Tool Call: Create Task ("create task ...", "add task ...")
        if low.startswith("create task") or low.startswith("add task"):
            task_title = low.replace("create task", "", 1).replace("add task", "", 1).replace(":", "").strip()
            if not task_title:
                task_title = "New Task"
            priority = "high" if "urgent" in low or "!high" in low else ("low" if "!low" in low else "medium")
            created = self.tool_create_task(db, user_id, title=task_title, priority=priority)
            return ChatResponse(
                reply=f"✅ Created task: **{created['title']}** (Priority: {created['priority'].capitalize()})",
                actions=[{"type": "navigate", "destination": "tasks"}],
                data={"task": created},
            )

        # 2. Tool Call: List Tasks ("show tasks", "list tasks", "my tasks", "what are my tasks")
        if any(w in low for w in ["show tasks", "list tasks", "my tasks", "what are my tasks", "view tasks"]):
            tasks = self.tool_get_user_tasks(db, user_id, limit=5)
            if not tasks:
                return ChatResponse(
                    reply="You don't have any tasks right now! You can ask me to create one (e.g. *'Create task: Complete API specs'*).",
                    actions=[{"type": "navigate", "destination": "tasks"}],
                )
            reply = f"Here are your upcoming tasks:\n\n"
            for idx, t in enumerate(tasks, 1):
                status_icon = "✅" if t["is_completed"] else "⏳"
                reply += f"{idx}. {status_icon} **{t['title']}** ({t['priority'].capitalize()})\n"
            return ChatResponse(
                reply=reply,
                actions=[{"type": "navigate", "destination": "tasks"}],
                data={"tasks": tasks},
            )

        # 3. Tool Call: Goals ("show goals", "my goals", "what are my goals", "list goals")
        if any(w in low for w in ["show goals", "my goals", "what are my goals", "list goals"]):
            goals = self.tool_get_user_goals(db, user_id)
            if not goals:
                return ChatResponse(
                    reply="You haven't set any long-term goals yet. Ask me *'Break down goal: Master Cybersecurity'* to get started!",
                    actions=[{"type": "navigate", "destination": "goals"}],
                )
            reply = f"Here are your current goals:\n\n"
            for idx, g in enumerate(goals, 1):
                reply += f"{idx}. 🎯 **{g['title']}** — {g['progress_percentage']}% completed\n"
            return ChatResponse(
                reply=reply,
                actions=[{"type": "navigate", "destination": "goals"}],
                data={"goals": goals},
            )

        # 4. Tool Call: Calendar ("calendar", "events today", "what is on my calendar", "schedule")
        if any(w in low for w in ["events today", "calendar events", "what's on my calendar"]):
            events = self.tool_get_calendar_events(db, user_id)
            if not events:
                return ChatResponse(
                    reply="You have no scheduled events on your calendar for today.",
                    actions=[{"type": "navigate", "destination": "calendar"}],
                )
            reply = "Here are your scheduled events for today:\n\n"
            for idx, ev in enumerate(events, 1):
                start_h = ev["start_time"].split("T")[1][:5]
                end_h = ev["end_time"].split("T")[1][:5]
                reply += f"{idx}. 📅 **{ev['title']}** ({start_h} - {end_h})\n"
            return ChatResponse(
                reply=reply,
                actions=[{"type": "navigate", "destination": "calendar"}],
                data={"events": events},
            )

        # 5. "Plan my day" / "Schedule today"
        if any(w in low for w in ["plan my day", "schedule today", "daily schedule", "plan today"]):
            plan = ai_service.daily_schedule(db, user_id)
            scheduled = plan.get("scheduled", [])
            unscheduled = plan.get("unscheduled", [])
            total_min = plan.get("total_work_minutes", 0)

            if not scheduled and not unscheduled:
                return ChatResponse(
                    reply="You don't have any pending tasks to schedule today! Would you like to create some tasks or review your long-term goals?",
                    actions=[{"type": "navigate", "destination": "tasks"}],
                )

            reply = (
                f"I've mapped out a day plan with {len(scheduled)} tasks totaling {round(total_min/60, 1)} hours "
                f"and {plan.get('break_minutes', 0)} minutes of scheduled cognitive breaks.\n\n"
            )
            for idx, item in enumerate(scheduled[:4], 1):
                start_h = item['start'].split("T")[1][:5]
                end_h = item['end'].split("T")[1][:5]
                reply += f"{idx}. **{item['title']}** ({start_h} - {end_h})\n"

            if len(scheduled) > 4:
                reply += f"...and {len(scheduled) - 4} more task(s).\n"

            if unscheduled:
                reply += f"\n⚠️ {len(unscheduled)} task(s) could not fit without exceeding your hours."

            return ChatResponse(
                reply=reply,
                actions=[
                    {"type": "confirm_schedule", "data": plan},
                    {"type": "navigate", "destination": "calendar"},
                ],
                data={"plan": plan},
            )

        # 6. "Overdue" / "What tasks are overdue?"
        if any(w in low for w in ["overdue", "late", "missed tasks"]):
            now = datetime.utcnow()
            overdue_tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.is_completed == False,
                    Task.due_date != None,
                    Task.due_date < now,
                    Task.status != "cancelled",
                )
                .all()
            )

            if not overdue_tasks:
                return ChatResponse(
                    reply="Great news! You have no overdue tasks at the moment. Everything is up to date.",
                    actions=[],
                )

            reply = f"You have {len(overdue_tasks)} overdue task(s):\n\n"
            for t in overdue_tasks[:5]:
                due_str = t.due_date.strftime("%b %d, %H:%M") if t.due_date else "Past"
                reply += f"- **{t.title}** (Was due: {due_str}, Priority: {t.priority.capitalize()})\n"

            reply += "\nWould you like me to find open slots to reschedule them?"
            return ChatResponse(
                reply=reply,
                actions=[
                    {"type": "reschedule_overdue", "task_ids": [t.id for t in overdue_tasks]},
                ],
                data={"overdue_count": len(overdue_tasks)},
            )

        # 7. "How is my productivity?" / "Productivity insights" / "Stats"
        if any(w in low for w in ["productivity", "score", "how am i doing", "coach", "insights", "analyze"]):
            insights_res = productivity_coach.analyze(db, user_id)
            reply = f"📊 **Productivity Score: {insights_res.overall_score}/100**\n\n{insights_res.summary}\n\n**Key Observations:**\n"
            for ins in insights_res.insights[:3]:
                prefix = "💡" if ins.priority == "suggestion" else ("⚠️" if ins.priority == "warning" else "✨")
                reply += f"{prefix} **{ins.title}**: {ins.description}\n\n"

            return ChatResponse(
                reply=reply,
                actions=[{"type": "navigate", "destination": "analytics"}],
                data={"insights": insights_res.model_dump()},
            )

        # 8. "Break down goal"
        if "break down" in low or "breakdown" in low:
            cleaned = low.replace("break down", "").replace("breakdown", "").replace("goal", "").replace(":", "").strip()
            title = cleaned if cleaned else "Mastering My Skills"
            breakdown = self.break_down_goal(title)
            reply = f"Here is a recommended milestone breakdown for **{breakdown.goal_title}**:\n\n"
            for idx, m in enumerate(breakdown.milestones, 1):
                reply += f"{idx}. **{m.title}** (~{m.estimated_days} days)\n"

            reply += "\nWould you like to apply these milestones to your goal tracker?"
            return ChatResponse(
                reply=reply,
                actions=[{"type": "create_goal_with_milestones", "data": breakdown.model_dump()}],
                data=breakdown.model_dump(),
            )

        # 9. Default natural conversational reply
        return ChatResponse(
            reply=(
                "I'm PlanWise AI, your personal productivity architect.\n\n"
                "Here are a few things you can ask me to do:\n"
                "• *'Create task: Review project architecture'* to add a task\n"
                "• *'Show tasks'* to list your current workload\n"
                "• *'Plan my day'* to generate an energy-balanced schedule\n"
                "• *'What tasks are overdue?'* to audit late tasks\n"
                "• *'How is my productivity?'* for personalized coaching insights\n"
                "• *'Break down goal: Become a Cybersecurity Specialist'* to generate milestones"
            ),
            actions=[
                {"type": "suggest_prompt", "text": "Plan my day"},
                {"type": "suggest_prompt", "text": "Show tasks"},
                {"type": "suggest_prompt", "text": "What tasks are overdue?"},
                {"type": "suggest_prompt", "text": "How is my productivity?"},
            ],
        )

    def break_down_goal(
        self, goal_title: str, goal_description: str = "", category: str = "Personal"
    ) -> GoalBreakdownResponse:
        low = goal_title.lower()

        # Heuristic milestone generation for common domains
        if any(w in low for w in ["cyber", "security", "pentest", "soc"]):
            milestones = [
                MilestoneSuggestion(title="Master Networking Fundamentals & OSI Model", estimated_days=14, order=0),
                MilestoneSuggestion(title="Linux Command Line & Privilege Audits", estimated_days=14, order=1),
                MilestoneSuggestion(title="Hands-on Labs (OverTheWire, TryHackMe)", estimated_days=21, order=2),
                MilestoneSuggestion(title="Vulnerability Assessment & Reporting Project", estimated_days=21, order=3),
                MilestoneSuggestion(title="Security Certification Prep (e.g. CompTIA Security+)", estimated_days=30, order=4),
            ]
        elif any(w in low for w in ["python", "code", "programming", "software", "developer"]):
            milestones = [
                MilestoneSuggestion(title="Language Core, Data Structures & Algorithms", estimated_days=14, order=0),
                MilestoneSuggestion(title="Build Fast & Resilient APIs with FastAPI", estimated_days=14, order=1),
                MilestoneSuggestion(title="Database Architecture (SQLAlchemy & Migrations)", estimated_days=10, order=2),
                MilestoneSuggestion(title="Full-Stack Integration Project with Testing", estimated_days=21, order=3),
                MilestoneSuggestion(title="Open-Source Portfolio Deployment & Showcase", estimated_days=14, order=4),
            ]
        elif any(w in low for w in ["fit", "gym", "health", "weight", "run"]):
            milestones = [
                MilestoneSuggestion(title="Establish baseline metrics & clean diet routine", estimated_days=7, order=0),
                MilestoneSuggestion(title="Consistent 3x/week workout habit for 4 weeks", estimated_days=28, order=1),
                MilestoneSuggestion(title="Intermediate progression & hydration tracking", estimated_days=30, order=2),
                MilestoneSuggestion(title="Measure milestones and calibrate maintenance phase", estimated_days=14, order=3),
            ]
        else:
            milestones = [
                MilestoneSuggestion(title=f"Phase 1: Research and foundation for {goal_title}", estimated_days=7, order=0),
                MilestoneSuggestion(title=f"Phase 2: Core skill acquisition and initial drafts", estimated_days=14, order=1),
                MilestoneSuggestion(title=f"Phase 3: Execution, practice, and iterative improvements", estimated_days=21, order=2),
                MilestoneSuggestion(title=f"Phase 4: Final delivery, review, and reflection", estimated_days=7, order=3),
            ]

        total_days = sum(m.estimated_days for m in milestones)
        return GoalBreakdownResponse(
            goal_title=goal_title,
            milestones=milestones,
            estimated_total_days=total_days,
            recommendations=[
                "Break milestones into 30-45 minute daily focus blocks.",
                "Review progress weekly to calibrate deadlines.",
            ],
        )


chat_agent = ChatAgent()
