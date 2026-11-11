from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.ai.agents.chat_agent import chat_agent
from backend.app.ai.agents.productivity_coach import productivity_coach
from backend.app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    GoalBreakdownRequest,
    GoalBreakdownResponse,
    ProductivityInsightsResponse,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Conversational AI Assistant. Parses natural language commands (e.g. 'plan my day',
    'what tasks are overdue?', 'how is my productivity?') and suggests actionable plans.
    """
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


@router.post("/goal-breakdown", response_model=GoalBreakdownResponse)
def break_down_goal(
    payload: GoalBreakdownRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Intelligently breaks down high-level aspirations or long-term goals into
    actionable, step-by-step milestones.
    """
    if not payload.goal_title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal title cannot be empty",
        )
    return chat_agent.break_down_goal(
        goal_title=payload.goal_title,
        goal_description=payload.goal_description,
        category=payload.category,
    )


@router.get("/productivity-insights", response_model=ProductivityInsightsResponse)
def get_productivity_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves personalized productivity coach analysis, identifying prime focus windows,
    streak consistency, and workload balance based on real user activity.
    """
    return productivity_coach.analyze(db=db, user_id=current_user.id)
