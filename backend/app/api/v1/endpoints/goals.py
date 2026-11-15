from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse
)
from backend.app.services.goal_service import goal_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("", response_model=List[GoalResponse], summary="List long-term goals with milestone progress")
def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.get_goals(db=db, user_id=current_user.id)

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED, summary="Create a long-term goal with milestones")
def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.create_goal(db=db, user_id=current_user.id, goal_in=goal_in)

@router.get("/{goal_id}", response_model=GoalResponse, summary="Get a single goal by ID")
def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.get_goal(db=db, user_id=current_user.id, goal_id=goal_id)

@router.put("/{goal_id}", response_model=GoalResponse, summary="Update an existing goal")
def update_goal(
    goal_id: str,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.update_goal(db=db, user_id=current_user.id, goal_id=goal_id, goal_in=goal_in)

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a goal and its milestones")
def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal_service.delete_goal(db=db, user_id=current_user.id, goal_id=goal_id)
    return None

# ── Goal Milestones / Tasks ──────────────────────────────────────────────────

@router.post("/{goal_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED, summary="Add a milestone/task to a goal")
def add_milestone(
    goal_id: str,
    milestone_in: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.add_milestone(db=db, user_id=current_user.id, goal_id=goal_id, milestone_in=milestone_in)

@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse, summary="Update a milestone/task")
def update_milestone(
    milestone_id: str,
    milestone_in: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.update_milestone(db=db, user_id=current_user.id, milestone_id=milestone_id, milestone_in=milestone_in)

@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a milestone/task")
def delete_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal_service.delete_milestone(db=db, user_id=current_user.id, milestone_id=milestone_id)
    return None

@router.post("/milestones/{milestone_id}/toggle", response_model=MilestoneResponse, summary="Toggle milestone completion")
def toggle_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.toggle_milestone(db=db, user_id=current_user.id, milestone_id=milestone_id)

# Compatibility route for /goals/{goal_id}/milestones/{milestone_id}/toggle
@router.put("/{goal_id}/milestones/{milestone_id}/toggle", response_model=MilestoneResponse, summary="Toggle milestone (compat)")
@router.post("/{goal_id}/milestones/{milestone_id}/toggle", response_model=MilestoneResponse, summary="Toggle milestone (compat)")
def toggle_milestone_compat(
    goal_id: str,
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return goal_service.toggle_milestone(db=db, user_id=current_user.id, milestone_id=milestone_id)
