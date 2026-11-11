from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.focus import FocusSessionCreate, FocusSessionResponse, FocusStatsResponse
from backend.app.services.focus_service import focus_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("/sessions", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED, summary="Record a completed Pomodoro/Focus interval")
def record_focus_session(
    session_in: FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return focus_service.record_session(db=db, user_id=current_user.id, session_in=session_in)

@router.get("/stats", response_model=FocusStatsResponse, summary="Get focus metrics for today and this week")
def get_focus_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return focus_service.get_focus_stats(db=db, user_id=current_user.id)
