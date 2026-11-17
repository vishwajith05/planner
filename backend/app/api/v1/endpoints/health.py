from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.database.session import get_db

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

@router.get("/health/db", summary="Database connectivity and integrity check")
def db_health_check(db: Session = Depends(get_db)):
    """Check database connectivity and report basic stats for diagnosing data loss."""
    try:
        # Verify DB is reachable
        db.execute(text("SELECT 1"))

        # Count users to detect DB resets
        from backend.app.models.user import User
        from backend.app.models.task import Task
        user_count = db.query(User).count()
        task_count = db.query(Task).count()

        return {
            "status": "healthy",
            "database": "connected",
            "database_url_type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
            "user_count": user_count,
            "task_count": task_count,
            "warning": "Database appears empty — data may have been reset" if user_count == 0 else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
