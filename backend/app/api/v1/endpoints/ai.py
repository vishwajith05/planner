from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.ai_service import ai_service
from backend.app.ai.agents.chat_agent import chat_agent
from backend.app.schemas.ai import (
    QuickAddRequest,
    QuickAddResponse,
    DailyScheduleRequest,
    DailyScheduleResponse,
    WeeklyPlanRequest,
    WeeklyPlanResponse,
    RescheduleRequest,
    RescheduleResponse,
    WorkloadAnalysisResponse,
    ChatRequest,
    ChatResponse,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Agentic Chat Assistant")
def chat_endpoint(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    return chat_agent.handle_message(
        db=db,
        user_id=current_user.id,
        message=payload.message,
    )


@router.post("/parse-task", response_model=QuickAddResponse)
async def parse_quick_add_task(
    payload: QuickAddRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Parses a natural language task description into structured task fields.
    Does NOT create a task directly; user confirms before creation.
    """
    if not payload.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty"
        )
    result = await ai_service.parse_quick_add(payload.prompt)
    return result


@router.post("/daily-schedule", response_model=DailyScheduleResponse)
@router.post("/schedule/daily", response_model=DailyScheduleResponse)
def generate_daily_schedule(
    payload: Optional[DailyScheduleRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates a conflict-free, energy-balanced daily schedule.
    Returns preview data for user confirmation.
    """
    p = payload or DailyScheduleRequest()
    result = ai_service.daily_schedule(
        db=db,
        user_id=current_user.id,
        date=p.date,
        day_start_hour=p.day_start_hour,
        day_end_hour=p.day_end_hour,
    )
    return result


@router.post("/weekly-plan", response_model=WeeklyPlanResponse)
@router.post("/schedule/weekly", response_model=WeeklyPlanResponse)
def generate_weekly_plan(
    payload: Optional[WeeklyPlanRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Distributes pending tasks across a 7-day week balancing daily workload.
    """
    p = payload or WeeklyPlanRequest()
    result = ai_service.weekly_plan(
        db=db,
        user_id=current_user.id,
        week_start=p.week_start,
        day_start_hour=p.day_start_hour,
        day_end_hour=p.day_end_hour,
        rest_days=p.rest_days,
        max_minutes_per_day=p.max_minutes_per_day,
    )
    return result


@router.post("/reschedule", response_model=RescheduleResponse)
def suggest_rescheduling(
    payload: RescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Detects overdue/missed tasks and suggests optimal alternative slots.
    """
    result = ai_service.reschedule(
        db=db,
        user_id=current_user.id,
        days_ahead=payload.days_ahead,
        day_start_hour=payload.day_start_hour,
        day_end_hour=payload.day_end_hour,
    )
    return result


@router.get("/workload-analysis", response_model=WorkloadAnalysisResponse)
def get_workload_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyzes pending tasks, overloads, and delivers proactive schedule warnings.
    """
    return ai_service.workload_analysis(db=db, user_id=current_user.id)
