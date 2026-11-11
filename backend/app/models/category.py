from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from datetime import datetime
import uuid
from backend.app.database.session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)  # null = system default
    name = Column(String, nullable=False)
    color = Column(String, default="#6366F1")
    icon = Column(String, default="folder")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
