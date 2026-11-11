from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List
import uuid

from backend.app.models.focus import FocusSession
from backend.app.schemas.focus import FocusSessionCreate, FocusStatsResponse

class FocusService:
    def record_session(self, db: Session, user_id: str, session_in: FocusSessionCreate) -> FocusSession:
        now = datetime.utcnow()
        session = FocusSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            task_id=session_in.task_id,
            duration_minutes=session_in.duration_minutes,
            session_type=session_in.session_type,
            completed=session_in.completed,
            notes=session_in.notes,
            started_at=session_in.started_at or (now - timedelta(minutes=session_in.duration_minutes)),
            ended_at=session_in.ended_at or now
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_focus_stats(self, db: Session, user_id: str) -> FocusStatsResponse:
        today_start = datetime.combine(date.today(), datetime.min.time())
        week_start = today_start - timedelta(days=today_start.weekday())

        today_sessions = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.completed == True,
            FocusSession.started_at >= today_start
        ).all()

        week_sessions = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.completed == True,
            FocusSession.started_at >= week_start
        ).all()

        return FocusStatsResponse(
            total_focus_minutes_today=sum(s.duration_minutes for s in today_sessions if s.session_type == "focus"),
            total_sessions_today=len(today_sessions),
            total_focus_minutes_this_week=sum(s.duration_minutes for s in week_sessions if s.session_type == "focus"),
            total_sessions_this_week=len(week_sessions)
        )

focus_service = FocusService()
