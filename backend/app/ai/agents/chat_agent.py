"""
Conversational AI Agent — Natural language productivity assistant.
Can process natural queries, inspect user state, generate action proposals
(such as schedule daily, reschedule overdue, break down goals), and deliver
conversational coaching.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List

from backend.app.models.task import Task
from backend.app.models.goal import Goal
from backend.app.services.ai_service import ai_service
from backend.app.ai.agents.productivity_coach import productivity_coach
from backend.app.schemas.ai import ChatResponse, GoalBreakdownResponse, MilestoneSuggestion


class ChatAgent:
    def handle_message(self, db: Session, user_id: str, message: str) -> ChatResponse:
        low = message.strip().lower()

        # 1. "Plan my day" / "Schedule today"
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

        # 2. "Overdue" / "What tasks are overdue?"
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

        # 3. "How is my productivity?" / "Productivity insights" / "Stats"
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

        # 4. "Break down goal"
        if "break down" in low or "goal" in low:
            # Check for a specific goal title
            cleaned = low.replace("break down", "").replace("goal", "").replace(":", "").strip()
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

        # 5. Default natural conversational reply
        return ChatResponse(
            reply=(
                "I'm PlanWise AI, your personal productivity architect.\n\n"
                "Here are a few things you can ask me to do:\n"
                "• *'Plan my day'* to generate an energy-balanced schedule\n"
                "• *'What tasks are overdue?'* to audit late tasks\n"
                "• *'How is my productivity?'* for personalized coaching insights\n"
                "• *'Break down goal: Become a Cybersecurity Specialist'* to generate milestones"
            ),
            actions=[
                {"type": "suggest_prompt", "text": "Plan my day"},
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
