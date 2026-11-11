"""
Sync Service — Handles batch offline synchronization, conflict resolution
using timestamp-based Last-Write-Wins (LWW), and delta changes retrieval.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from backend.app.models.task import Task
from backend.app.models.habit import Habit, HabitCompletion
from backend.app.models.focus import FocusSession
from backend.app.models.goal import Goal, Milestone
from backend.app.schemas.sync import (
    SyncMutation,
    MutationResult,
    SyncPushResponse,
    SyncPullResponse,
    FullSyncResponse,
)


class SyncService:
    def process_push(
        self, db: Session, user_id: str, mutations: List[SyncMutation]
    ) -> SyncPushResponse:
        results: List[MutationResult] = []
        applied = 0
        conflicts = 0
        server_now = datetime.utcnow()

        for m in mutations:
            try:
                res = self._apply_mutation(db, user_id, m, server_now)
                results.append(res)
                if res.status == "applied":
                    applied += 1
                elif res.status == "conflict_server_wins":
                    conflicts += 1
            except Exception as e:
                results.append(
                    MutationResult(
                        mutation_id=m.id,
                        entity_type=m.entity_type,
                        entity_id=m.entity_id,
                        status="error",
                        message=str(e),
                    )
                )

        db.commit()

        return SyncPushResponse(
            applied_count=applied,
            conflict_count=conflicts,
            results=results,
            server_timestamp=server_now,
        )

    def _apply_mutation(
        self, db: Session, user_id: str, m: SyncMutation, server_now: datetime
    ) -> MutationResult:
        if m.entity_type == "task":
            return self._apply_task_mutation(db, user_id, m, server_now)
        elif m.entity_type == "habit":
            return self._apply_habit_mutation(db, user_id, m, server_now)
        elif m.entity_type == "focus":
            return self._apply_focus_mutation(db, user_id, m, server_now)
        else:
            return MutationResult(
                mutation_id=m.id,
                entity_type=m.entity_type,
                entity_id=m.entity_id,
                status="error",
                message=f"Unsupported entity type: {m.entity_type}",
            )

    def _apply_task_mutation(
        self, db: Session, user_id: str, m: SyncMutation, server_now: datetime
    ) -> MutationResult:
        existing = db.query(Task).filter(Task.id == m.entity_id, Task.user_id == user_id).first()

        if m.action == "create":
            if existing:
                # Already exists; treat as update or skip
                return MutationResult(
                    mutation_id=m.id,
                    entity_type="task",
                    entity_id=m.entity_id,
                    status="applied",
                    message="Entity already present on server",
                )
            d = m.data or {}
            new_task = Task(
                id=m.entity_id or str(uuid.uuid4()),
                user_id=user_id,
                title=d.get("title", "Untitled Task"),
                description=d.get("description"),
                notes=d.get("notes"),
                priority=d.get("priority", "medium"),
                status=d.get("status", "not_started"),
                category=d.get("category", "Personal"),
                tags=d.get("tags", ""),
                list_name=d.get("list_name", "Inbox"),
                estimated_minutes=d.get("estimated_minutes", 30),
                actual_minutes=d.get("actual_minutes", 0),
                is_completed=d.get("is_completed", False),
                subtasks=d.get("subtasks", []),
                created_at=m.client_timestamp,
                updated_at=server_now,
            )
            db.add(new_task)
            return MutationResult(
                mutation_id=m.id, entity_type="task", entity_id=new_task.id, status="applied"
            )

        elif m.action in ("update", "toggle"):
            if not existing:
                return MutationResult(
                    mutation_id=m.id,
                    entity_type="task",
                    entity_id=m.entity_id,
                    status="error",
                    message="Task not found on server to update",
                )

            # LWW Conflict Check: if server version is strictly newer than client timestamp
            if existing.updated_at and existing.updated_at > m.client_timestamp:
                return MutationResult(
                    mutation_id=m.id,
                    entity_type="task",
                    entity_id=m.entity_id,
                    status="conflict_server_wins",
                    message="Server has a more recent modification.",
                )

            # Apply update
            if m.action == "toggle":
                existing.is_completed = not existing.is_completed
                existing.status = "completed" if existing.is_completed else "in_progress"
                existing.completed_at = server_now if existing.is_completed else None
            elif m.data:
                for k, v in m.data.items():
                    if hasattr(existing, k) and k not in ("id", "user_id"):
                        setattr(existing, k, v)

            existing.updated_at = server_now
            return MutationResult(
                mutation_id=m.id, entity_type="task", entity_id=existing.id, status="applied"
            )

        elif m.action == "delete":
            if existing:
                db.delete(existing)
            return MutationResult(
                mutation_id=m.id, entity_type="task", entity_id=m.entity_id, status="applied"
            )

        return MutationResult(
            mutation_id=m.id,
            entity_type="task",
            entity_id=m.entity_id,
            status="error",
            message=f"Unknown action: {m.action}",
        )

    def _apply_habit_mutation(
        self, db: Session, user_id: str, m: SyncMutation, server_now: datetime
    ) -> MutationResult:
        if m.action == "toggle":
            # Toggle habit completion for a specific date
            d = m.data or {}
            completion_date = d.get("completion_date", server_now.strftime("%Y-%m-%d"))
            existing_comp = (
                db.query(HabitCompletion)
                .filter(
                    HabitCompletion.habit_id == m.entity_id,
                    HabitCompletion.user_id == user_id,
                    HabitCompletion.completion_date == completion_date,
                )
                .first()
            )
            habit = db.query(Habit).filter(Habit.id == m.entity_id, Habit.user_id == user_id).first()
            if existing_comp:
                db.delete(existing_comp)
                if habit and habit.streak_count > 0:
                    habit.streak_count -= 1
            else:
                db.add(
                    HabitCompletion(
                        id=str(uuid.uuid4()),
                        habit_id=m.entity_id,
                        user_id=user_id,
                        completion_date=completion_date,
                    )
                )
                if habit:
                    habit.streak_count += 1
                    if habit.streak_count > habit.best_streak:
                        habit.best_streak = habit.streak_count

            return MutationResult(
                mutation_id=m.id, entity_type="habit", entity_id=m.entity_id, status="applied"
            )
        return MutationResult(
            mutation_id=m.id, entity_type="habit", entity_id=m.entity_id, status="applied"
        )

    def _apply_focus_mutation(
        self, db: Session, user_id: str, m: SyncMutation, server_now: datetime
    ) -> MutationResult:
        if m.action == "create":
            d = m.data or {}
            session = FocusSession(
                id=m.entity_id or str(uuid.uuid4()),
                user_id=user_id,
                duration_minutes=d.get("duration_minutes", 25),
                session_type=d.get("session_type", "focus"),
                completed=d.get("completed", True),
                notes=d.get("notes"),
                started_at=m.client_timestamp,
                ended_at=server_now,
            )
            db.add(session)
            return MutationResult(
                mutation_id=m.id, entity_type="focus", entity_id=session.id, status="applied"
            )
        return MutationResult(
            mutation_id=m.id, entity_type="focus", entity_id=m.entity_id, status="applied"
        )

    def process_pull(
        self, db: Session, user_id: str, last_synced_at: Optional[datetime] = None
    ) -> SyncPullResponse:
        server_now = datetime.utcnow()

        task_q = db.query(Task).filter(Task.user_id == user_id)
        habit_q = db.query(Habit).filter(Habit.user_id == user_id)
        focus_q = db.query(FocusSession).filter(FocusSession.user_id == user_id)
        goal_q = db.query(Goal).filter(Goal.user_id == user_id)

        if last_synced_at:
            task_q = task_q.filter(Task.updated_at >= last_synced_at)
            habit_q = habit_q.filter(Habit.updated_at >= last_synced_at)
            focus_q = focus_q.filter(FocusSession.started_at >= last_synced_at)
            goal_q = goal_q.filter(Goal.updated_at >= last_synced_at)

        tasks = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "status": t.status,
                "category": t.category,
                "estimated_minutes": t.estimated_minutes,
                "is_completed": t.is_completed,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in task_q.all()
        ]

        habits = [
            {
                "id": h.id,
                "title": h.title,
                "category": h.category,
                "streak_count": h.streak_count,
                "best_streak": h.best_streak,
            }
            for h in habit_q.all()
        ]

        focus = [
            {
                "id": f.id,
                "duration_minutes": f.duration_minutes,
                "session_type": f.session_type,
                "started_at": f.started_at.isoformat() if f.started_at else None,
            }
            for f in focus_q.all()
        ]

        goals = [
            {
                "id": g.id,
                "title": g.title,
                "category": g.category,
                "status": g.status,
                "progress_percentage": g.progress_percentage,
            }
            for g in goal_q.all()
        ]

        return SyncPullResponse(
            server_timestamp=server_now,
            tasks=tasks,
            habits=habits,
            focus_sessions=focus,
            goals=goals,
        )

    def full_sync(
        self,
        db: Session,
        user_id: str,
        mutations: List[SyncMutation],
        last_synced_at: Optional[datetime] = None,
    ) -> FullSyncResponse:
        push_res = self.process_push(db, user_id, mutations)
        pull_res = self.process_pull(db, user_id, last_synced_at)
        return FullSyncResponse(push_results=push_res, pull_data=pull_res)


sync_service = SyncService()
