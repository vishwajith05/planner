from fastapi import APIRouter
from backend.app.schemas.dashboard import DashboardSummaryResponse
from backend.app.services.dashboard_service import dashboard_service

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse, summary="Get dashboard summary metrics and tasks")
async def get_dashboard_summary():
    return await dashboard_service.get_dashboard_summary()
