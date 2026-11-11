from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    dashboard,
    auth,
    tasks,
    calendar,
    habits,
    focus,
    goals,
    analytics,
    ai,
    ai_chat
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar & Time Blocking"])
api_router.include_router(habits.router, prefix="/habits", tags=["Habits"])
api_router.include_router(focus.router, prefix="/focus", tags=["Focus & Pomodoro"])
api_router.include_router(goals.router, prefix="/goals", tags=["Goals & Milestones"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Insights"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Engine"])
api_router.include_router(ai_chat.router, prefix="/ai/assistant", tags=["AI Assistant & Coach"])
