from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database.session import get_db
from backend.app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventResponse,
    ConflictCheckRequest,
    ConflictCheckResponse
)
from backend.app.services.calendar_service import calendar_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/events", response_model=List[CalendarEventResponse], summary="List calendar events and time-blocks")
def get_events(
    start_time: Optional[datetime] = Query(None, description="Filter events after start_time"),
    end_time: Optional[datetime] = Query(None, description="Filter events before end_time"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return calendar_service.get_events(db=db, user_id=current_user.id, start_time=start_time, end_time=end_time)

@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED, summary="Schedule a new calendar time-block")
def create_event(
    event_in: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return calendar_service.create_event(db=db, user_id=current_user.id, event_in=event_in)

@router.post("/check-conflicts", response_model=ConflictCheckResponse, summary="Detect overlapping time slots or fixed commitment clashes")
def check_conflicts(
    req: ConflictCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return calendar_service.check_conflicts(
        db=db,
        user_id=current_user.id,
        start_time=req.start_time,
        end_time=req.end_time,
        ignore_event_id=req.ignore_event_id
    )

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete calendar event")
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calendar_service.delete_event(db=db, user_id=current_user.id, event_id=event_id)
    return None
