from backend.app.schemas.dashboard import DashboardSummaryResponse, TaskSummaryItem
from backend.app.ai.providers.mock_provider import MockAIProvider

class DashboardService:
    def __init__(self):
        self.ai_provider = MockAIProvider()

    async def get_dashboard_summary(self, user_id: str = "guest") -> DashboardSummaryResponse:
        # Sample items for Phase 1 baseline verification
        sample_tasks = [
            TaskSummaryItem(
                id="1",
                title="Review Cybersecurity Network Security Architecture",
                time="09:00 AM - 10:30 AM",
                category="Cybersecurity",
                priority="urgent",
                is_completed=True
            ),
            TaskSummaryItem(
                id="2",
                title="Implement FastAPI Deterministic Scheduler Engine",
                time="11:00 AM - 12:30 PM",
                category="Programming",
                priority="high",
                is_completed=False
            ),
            TaskSummaryItem(
                id="3",
                title="Deep Work: Flutter State Management & Clean Architecture",
                time="02:00 PM - 03:30 PM",
                category="Education",
                priority="medium",
                is_completed=False
            ),
            TaskSummaryItem(
                id="4",
                title="Evening Physical Conditioning & Hydration",
                time="06:00 PM - 06:45 PM",
                category="Health",
                priority="low",
                is_completed=False
            ),
        ]

        tip = await self.ai_provider.get_productivity_tip({"score": 84})

        return DashboardSummaryResponse(
            greeting="Good day, Architect",
            productivity_score=84,
            productivity_status="Optimal Pace",
            ai_tip=tip,
            completed_tasks_count=5,
            pending_tasks_count=3,
            focus_minutes_today=75,
            active_habits_count=4,
            today_tasks=sample_tasks
        )

dashboard_service = DashboardService()
