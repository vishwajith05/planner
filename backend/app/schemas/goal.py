from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    target_date: Optional[datetime] = None
    is_completed: bool = False
    order_index: int = 0

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    target_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    order_index: Optional[int] = None

class MilestoneResponse(MilestoneBase):
    id: str
    goal_id: str
    user_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    goal_progress: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = "Personal"
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    target_date: Optional[datetime] = None
    status: str = Field(default="in_progress", pattern="^(in_progress|completed|paused)$")

class GoalCreate(GoalBase):
    milestones: List[MilestoneCreate] = Field(default_factory=list)

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    target_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|paused)$")
    progress_percentage: Optional[float] = None

class GoalResponse(GoalBase):
    id: str
    user_id: str
    progress_percentage: float
    milestones: List[MilestoneResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
