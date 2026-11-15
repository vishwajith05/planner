from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user_optional
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardSummaryResponse
from backend.app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/", response_model=DashboardSummaryResponse, summary="Get dashboard summary metrics and tasks")
@router.get("/summary", response_model=DashboardSummaryResponse, summary="Get dashboard summary metrics and tasks")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else "guest"
    return await dashboard_service.get_dashboard_summary(db=db, user_id=user_id)
