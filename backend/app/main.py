import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from backend.app.api.v1.api import api_router
from backend.app.database.session import engine, Base, SessionLocal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create tables if not existing
Base.metadata.create_all(bind=engine)

# Startup data integrity check — log how many users/tables exist
try:
    from backend.app.models.user import User
    db = SessionLocal()
    user_count = db.query(User).count()
    table_names = Base.metadata.tables.keys()
    logger.info(f"[STARTUP] Database has {user_count} users across {len(table_names)} tables: {list(table_names)}")
    if user_count == 0:
        logger.warning("[STARTUP] Database is EMPTY — no users found. If this is unexpected, the DB file may have been reset.")
    db.close()
except Exception as e:
    logger.error(f"[STARTUP] Database integrity check failed: {e}")

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
