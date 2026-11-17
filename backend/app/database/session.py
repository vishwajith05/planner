import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL

# Fix postgres:// → postgresql:// for SQLAlchemy 2.x
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# For SQLite: ensure the database file is in a persistent directory
# On Render, use a persistent data directory; locally, use ./data/
if db_url.startswith("sqlite:///") and "memory" not in db_url:
    # Extract relative path from sqlite:///./planwise.db → planwise.db
    raw_path = db_url.replace("sqlite:///", "")
    db_filename = os.path.basename(raw_path) or "planwise.db"

    # Use persistent directory: RENDER_PERSISTENT_DIR on Render, or ./data/ locally
    persistent_dir = os.environ.get("RENDER_PERSISTENT_DIR")
    if persistent_dir:
        data_dir = os.path.join(persistent_dir, "db")
    else:
        data_dir = os.path.join(os.getcwd(), "data")

    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, db_filename)
    db_url = f"sqlite:///{db_path}"
    logger.info(f"SQLite database path: {db_path}")

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
