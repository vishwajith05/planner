from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from backend.app.models.calendar_event import CalendarEvent
from backend.app.schemas.calendar import CalendarEventCreate, TimeConflict, ConflictCheckResponse

class CalendarService:
    def get_events(
        self,
        db: Session,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        query = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
        if start_time:
            query = query.filter(CalendarEvent.end_time >= start_time)
        if end_time:
            query = query.filter(CalendarEvent.start_time <= end_time)
        return query.order_by(CalendarEvent.start_time.asc()).all()

    def check_conflicts(
        self,
        db: Session,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        ignore_event_id: Optional[str] = None
    ) -> ConflictCheckResponse:
        # Overlap condition: (existing.start < proposed.end) and (existing.end > proposed.start)
        query = db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time < end_time,
            CalendarEvent.end_time > start_time
        )
        if ignore_event_id:
            query = query.filter(CalendarEvent.id != ignore_event_id)

        overlapping = query.all()
        conflicts = [
            TimeConflict(
                existing_event_id=e.id,
                existing_event_title=e.title,
                start_time=e.start_time,
                end_time=e.end_time,
                is_fixed=e.is_fixed,
                conflict_reason="Fixed commitment clash" if e.is_fixed else "Time slot overlap"
            )
            for e in overlapping
        ]
        return ConflictCheckResponse(has_conflict=len(conflicts) > 0, conflicts=conflicts)

    def create_event(self, db: Session, user_id: str, event_in: CalendarEventCreate) -> CalendarEvent:
        if event_in.end_time <= event_in.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event end_time must be later than start_time"
            )

        event = CalendarEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=event_in.title,
            description=event_in.description,
            start_time=event_in.start_time,
            end_time=event_in.end_time,
            is_fixed=event_in.is_fixed,
            task_id=event_in.task_id,
            category=event_in.category or "General"
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def delete_event(self, db: Session, user_id: str, event_id: str) -> None:
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == user_id).first()
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found")
        db.delete(event)
        db.commit()

calendar_service = CalendarService()
