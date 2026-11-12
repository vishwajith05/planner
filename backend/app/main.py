from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from backend.app.api.v1.api import api_router
from backend.app.database.session import engine, Base

# Create tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance AI-powered productivity engine & backend services for PlanWise AI.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# Security and Rate Limiting Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=30)

# CORS Middleware setup
cors_origins = list(settings.BACKEND_CORS_ORIGINS) if isinstance(settings.BACKEND_CORS_ORIGINS, (list, tuple)) else ["*"]
if "*" not in cors_origins:
    cors_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
@app.head("/")
async def root():
    return {
        "status": "healthy",
        "message": f"Welcome to {settings.PROJECT_NAME} Backend",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

@app.get("/health")
@app.get("/healthz")
@app.head("/health")
@app.head("/healthz")
async def root_health():
    return {"status": "healthy"}
