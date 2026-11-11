from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()

@router.get("/health", summary="Service health check")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "version": "1.0.0"
    }
