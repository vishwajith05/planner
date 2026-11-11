from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database.session import get_db
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, CategoryResponse, CategoryCreate
from backend.app.services.task_service import task_service
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("", response_model=List[TaskResponse], summary="List and filter authenticated user tasks")
def list_tasks(
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, urgent"),
    status: Optional[str] = Query(None, description="Filter by status: not_started, in_progress, completed, cancelled"),
    is_completed: Optional[bool] = Query(None, description="Filter by completion flag"),
    search: Optional[str] = Query(None, description="Search keyword in title, description, notes, tags"),
    list_name: Optional[str] = Query(None, description="Filter by list name"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due on or before timestamp"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due on or after timestamp"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.get_tasks(
        db=db,
        user_id=current_user.id,
        category=category,
        priority=priority,
        status_val=status,
        is_completed=is_completed,
        search=search,
        list_name=list_name,
        due_before=due_before,
        due_after=due_after
    )

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.create_task(db=db, user_id=current_user.id, task_in=task_in)

@router.get("/categories", response_model=List[CategoryResponse], summary="Get default and user-defined categories")
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.get_categories(db=db, user_id=current_user.id)

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create a custom category")
def create_category(
    cat_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.create_category(db=db, user_id=current_user.id, cat_in=cat_in)

@router.get("/{task_id}", response_model=TaskResponse, summary="Retrieve a specific task by ID")
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.get_task_by_id(db=db, user_id=current_user.id, task_id=task_id)

@router.put("/{task_id}", response_model=TaskResponse, summary="Update an existing task")
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.update_task(db=db, user_id=current_user.id, task_id=task_id, task_in=task_in)

@router.post("/{task_id}/toggle", response_model=TaskResponse, summary="Toggle task completion status")
def toggle_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.toggle_task_completion(db=db, user_id=current_user.id, task_id=task_id)

@router.post("/{task_id}/duplicate", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Duplicate an existing task")
def duplicate_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return task_service.duplicate_task(db=db, user_id=current_user.id, task_id=task_id)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service.delete_task(db=db, user_id=current_user.id, task_id=task_id)
    return None
