from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from backend.app.models.task import Task
from backend.app.models.category import Category
from backend.app.schemas.task import TaskCreate, TaskUpdate, CategoryCreate

DEFAULT_CATEGORIES = [
    {"name": "Personal", "color": "#8B5CF6", "icon": "person"},
    {"name": "Work", "color": "#3B82F6", "icon": "work"},
    {"name": "Education", "color": "#10B981", "icon": "school"},
    {"name": "Programming", "color": "#06B6D4", "icon": "code"},
    {"name": "Cybersecurity", "color": "#EC4899", "icon": "security"},
    {"name": "Research", "color": "#F59E0B", "icon": "science"},
    {"name": "Entrepreneurship", "color": "#F97316", "icon": "business_center"},
    {"name": "Health", "color": "#14B8A6", "icon": "fitness_center"},
]

class TaskService:
    def get_tasks(
        self,
        db: Session,
        user_id: str,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status_val: Optional[str] = None,
        is_completed: Optional[bool] = None,
        search: Optional[str] = None,
        list_name: Optional[str] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
    ) -> List[Task]:
        query = db.query(Task).filter(Task.user_id == user_id)

        if category:
            query = query.filter(Task.category == category)
        if priority:
            query = query.filter(Task.priority == priority)
        if status_val:
            query = query.filter(Task.status == status_val)
        if is_completed is not None:
            query = query.filter(Task.is_completed == is_completed)
        if list_name:
            query = query.filter(Task.list_name == list_name)
        if due_before:
            query = query.filter(Task.due_date <= due_before)
        if due_after:
            query = query.filter(Task.due_date >= due_after)
        if search:
            search_fmt = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_fmt),
                    Task.description.ilike(search_fmt),
                    Task.notes.ilike(search_fmt),
                    Task.tags.ilike(search_fmt)
                )
            )

        return query.order_by(Task.is_completed.asc(), Task.due_date.asc().nulls_last(), Task.created_at.desc()).all()

    def get_task_by_id(self, db: Session, user_id: str, task_id: str) -> Task:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or access unauthorized"
            )
        return task

    def create_task(self, db: Session, user_id: str, task_in: TaskCreate) -> Task:
        # Convert subtasks list of pydantic models to list of dicts for JSON column
        subtasks_data = [s.model_dump() for s in task_in.subtasks] if task_in.subtasks else []

        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=task_in.title,
            description=task_in.description,
            notes=task_in.notes,
            priority=task_in.priority,
            status=task_in.status,
            category=task_in.category,
            tags=task_in.tags or "",
            list_name=task_in.list_name,
            estimated_minutes=task_in.estimated_minutes,
            actual_minutes=task_in.actual_minutes,
            start_time=task_in.start_time,
            due_date=task_in.due_date,
            reminder_time=task_in.reminder_time,
            recurrence=task_in.recurrence,
            subtasks=subtasks_data,
            is_completed=task_in.is_completed,
            completed_at=datetime.utcnow() if task_in.is_completed else None
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_task(self, db: Session, user_id: str, task_id: str, task_in: TaskUpdate) -> Task:
        task = self.get_task_by_id(db, user_id, task_id)
        update_data = task_in.model_dump(exclude_unset=True)

        if "subtasks" in update_data and update_data["subtasks"] is not None:
            update_data["subtasks"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in update_data["subtasks"]]

        if "is_completed" in update_data:
            if update_data["is_completed"] and not task.is_completed:
                task.completed_at = datetime.utcnow()
                task.status = "completed"
            elif not update_data["is_completed"] and task.is_completed:
                task.completed_at = None
                task.status = "in_progress"

        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)
        return task

    def toggle_task_completion(self, db: Session, user_id: str, task_id: str) -> Task:
        task = self.get_task_by_id(db, user_id, task_id)
        task.is_completed = not task.is_completed
        if task.is_completed:
            task.completed_at = datetime.utcnow()
            task.status = "completed"
        else:
            task.completed_at = None
            task.status = "in_progress"
        db.commit()
        db.refresh(task)
        return task

    def duplicate_task(self, db: Session, user_id: str, task_id: str) -> Task:
        original = self.get_task_by_id(db, user_id, task_id)
        duplicate = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=f"Copy of {original.title}",
            description=original.description,
            notes=original.notes,
            priority=original.priority,
            status="not_started",
            category=original.category,
            tags=original.tags,
            list_name=original.list_name,
            estimated_minutes=original.estimated_minutes,
            actual_minutes=0,
            start_time=original.start_time,
            due_date=original.due_date,
            reminder_time=original.reminder_time,
            recurrence=original.recurrence,
            subtasks=original.subtasks.copy() if original.subtasks else [],
            is_completed=False,
            completed_at=None
        )
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)
        return duplicate

    def delete_task(self, db: Session, user_id: str, task_id: str) -> None:
        task = self.get_task_by_id(db, user_id, task_id)
        db.delete(task)
        db.commit()

    def get_categories(self, db: Session, user_id: str) -> List[Category]:
        # Seed default categories if none exist in the database
        count = db.query(Category).count()
        if count == 0:
            for cat in DEFAULT_CATEGORIES:
                db.add(Category(
                    id=str(uuid.uuid4()),
                    name=cat["name"],
                    color=cat["color"],
                    icon=cat["icon"],
                    is_default=True
                ))
            db.commit()

        # Return global defaults + user custom categories
        return db.query(Category).filter(
            or_(Category.is_default == True, Category.user_id == user_id)
        ).all()

    def create_category(self, db: Session, user_id: str, cat_in: CategoryCreate) -> Category:
        existing = db.query(Category).filter(
            Category.name.ilike(cat_in.name),
            or_(Category.user_id == user_id, Category.is_default == True)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{cat_in.name}' already exists"
            )

        new_cat = Category(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=cat_in.name,
            color=cat_in.color or "#6366F1",
            icon=cat_in.icon or "folder",
            is_default=False
        )
        db.add(new_cat)
        db.commit()
        db.refresh(new_cat)
        return new_cat

task_service = TaskService()
