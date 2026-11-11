from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database.session import get_db
from backend.app.schemas.habit import (
    HabitCreate,
    HabitResponse,
    HabitToggleResponse,
    HabitStatsResponse
)
from backend.app.services.habit_service import habit_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("", response_model=List[HabitResponse], summary="List habits with daily completion states")
def list_habits(
    include_archived: bool = Query(False, description="Include archived habits"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return habit_service.get_habits(db=db, user_id=current_user.id, include_archived=include_archived)

@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED, summary="Create a new habit")
def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    h = habit_service.create_habit(db=db, user_id=current_user.id, habit_in=habit_in)
    return HabitResponse.model_validate(h)

@router.post("/{habit_id}/toggle", response_model=HabitToggleResponse, summary="Toggle habit completion and update streak")
def toggle_habit(
    habit_id: str,
    date_str: Optional[str] = Query(None, description="ISO date YYYY-MM-DD; defaults to today"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return habit_service.toggle_habit_today(db=db, user_id=current_user.id, habit_id=habit_id, for_date=date_str)

@router.get("/stats", response_model=HabitStatsResponse, summary="Get summary habit statistics and streak metrics")
def get_habit_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return habit_service.get_habit_stats(db=db, user_id=current_user.id)

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a habit")
def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    habit_service.delete_habit(db=db, user_id=current_user.id, habit_id=habit_id)
    return None
