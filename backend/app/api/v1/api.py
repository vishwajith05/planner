from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, dashboard, auth, tasks

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
