from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.analytics_service import analytics_service
from backend.app.schemas.analytics import AnalyticsSummary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    period: str = Query("this_week", description="today, this_week, this_month, or custom"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD for custom period"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD for custom period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns comprehensive analytics summary based on real user activity data.
    Supports periods: today, this_week, this_month, custom.
    """
    return analytics_service.get_summary(
        db=db,
        user_id=current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )
