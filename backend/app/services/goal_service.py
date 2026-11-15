from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from backend.app.models.goal import Goal, Milestone
from backend.app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse
)

class GoalService:
    def _recalc_goal_progress(self, db: Session, goal_id: str) -> None:
        milestones = db.query(Milestone).filter(Milestone.goal_id == goal_id).all()
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None
        if not milestones:
            goal.progress_percentage = 0.0
            db.commit()
            db.refresh(goal)
            return goal
        completed_count = sum(1 for m in milestones if m.is_completed)
        progress = (completed_count / len(milestones)) * 100.0
        goal.progress_percentage = round(progress, 1)
        if progress >= 100.0:
            goal.status = "completed"
        elif goal.status == "completed":
            goal.status = "in_progress"
        db.commit()
        db.refresh(goal)
        return goal

    def get_goals(self, db: Session, user_id: str) -> List[GoalResponse]:
        goals = db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.created_at.desc()).all()
        result = []
        for g in goals:
            milestones = db.query(Milestone).filter(
                Milestone.goal_id == g.id,
                Milestone.user_id == user_id
            ).order_by(Milestone.order_index.asc()).all()

            resp = GoalResponse.model_validate(g)
            resp.milestones = [MilestoneResponse.model_validate(m) for m in milestones]
            result.append(resp)
        return result

    def get_goal(self, db: Session, user_id: str, goal_id: str) -> GoalResponse:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        milestones = db.query(Milestone).filter(
            Milestone.goal_id == goal.id,
            Milestone.user_id == user_id
        ).order_by(Milestone.order_index.asc()).all()
        resp = GoalResponse.model_validate(goal)
        resp.milestones = [MilestoneResponse.model_validate(m) for m in milestones]
        return resp

    def create_goal(self, db: Session, user_id: str, goal_in: GoalCreate) -> GoalResponse:
        goal_id = str(uuid.uuid4())
        total_m = len(goal_in.milestones)
        completed_m = sum(1 for m in goal_in.milestones if m.is_completed)
        initial_progress = round((completed_m / total_m) * 100.0, 1) if total_m > 0 else 0.0
        status_val = "completed" if initial_progress >= 100.0 else goal_in.status

        goal = Goal(
            id=goal_id,
            user_id=user_id,
            title=goal_in.title,
            description=goal_in.description,
            category=goal_in.category or "Personal",
            priority=goal_in.priority or "medium",
            target_date=goal_in.target_date,
            status=status_val,
            progress_percentage=initial_progress
        )
        db.add(goal)

        milestones_created = []
        for idx, m in enumerate(goal_in.milestones):
            m_entity = Milestone(
                id=str(uuid.uuid4()),
                goal_id=goal_id,
                user_id=user_id,
                title=m.title,
                priority=m.priority or "medium",
                target_date=m.target_date,
                is_completed=m.is_completed,
                order_index=idx
            )
            db.add(m_entity)
            milestones_created.append(m_entity)

        db.commit()
        db.refresh(goal)

        resp = GoalResponse.model_validate(goal)
        resp.milestones = [MilestoneResponse.model_validate(m) for m in milestones_created]
        return resp

    def update_goal(self, db: Session, user_id: str, goal_id: str, goal_in: GoalUpdate) -> GoalResponse:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        if goal_in.title is not None:
            goal.title = goal_in.title
        if goal_in.description is not None:
            goal.description = goal_in.description
        if goal_in.category is not None:
            goal.category = goal_in.category
        if goal_in.priority is not None:
            goal.priority = goal_in.priority
        if goal_in.target_date is not None:
            goal.target_date = goal_in.target_date
        if goal_in.status is not None:
            goal.status = goal_in.status
        if goal_in.progress_percentage is not None:
            goal.progress_percentage = goal_in.progress_percentage

        db.commit()
        db.refresh(goal)
        return self.get_goal(db, user_id, goal_id)

    def delete_goal(self, db: Session, user_id: str, goal_id: str) -> None:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        db.query(Milestone).filter(Milestone.goal_id == goal_id).delete()
        db.delete(goal)
        db.commit()

    def add_milestone(self, db: Session, user_id: str, goal_id: str, milestone_in: MilestoneCreate) -> MilestoneResponse:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        current_count = db.query(Milestone).filter(Milestone.goal_id == goal_id).count()
        m_entity = Milestone(
            id=str(uuid.uuid4()),
            goal_id=goal_id,
            user_id=user_id,
            title=milestone_in.title,
            priority=milestone_in.priority or "medium",
            target_date=milestone_in.target_date,
            is_completed=milestone_in.is_completed,
            order_index=current_count
        )
        db.add(m_entity)
        db.commit()
        goal = self._recalc_goal_progress(db, goal_id)
        db.refresh(m_entity)
        res = MilestoneResponse.model_validate(m_entity)
        res.goal_progress = goal.progress_percentage if goal else 0
        return res

    def update_milestone(self, db: Session, user_id: str, milestone_id: str, milestone_in: MilestoneUpdate) -> MilestoneResponse:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id, Milestone.user_id == user_id).first()
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        if milestone_in.title is not None:
            milestone.title = milestone_in.title
        if milestone_in.priority is not None:
            milestone.priority = milestone_in.priority
        if milestone_in.target_date is not None:
            milestone.target_date = milestone_in.target_date
        if milestone_in.order_index is not None:
            milestone.order_index = milestone_in.order_index
        if milestone_in.is_completed is not None:
            milestone.is_completed = milestone_in.is_completed
            milestone.completed_at = datetime.utcnow() if milestone.is_completed else None

        db.commit()
        goal = self._recalc_goal_progress(db, milestone.goal_id)
        db.refresh(milestone)
        res = MilestoneResponse.model_validate(milestone)
        res.goal_progress = goal.progress_percentage if goal else 0
        return res

    def delete_milestone(self, db: Session, user_id: str, milestone_id: str) -> None:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id, Milestone.user_id == user_id).first()
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
        goal_id = milestone.goal_id
        db.delete(milestone)
        db.commit()
        self._recalc_goal_progress(db, goal_id)

    def toggle_milestone(self, db: Session, user_id: str, milestone_id: str) -> MilestoneResponse:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id, Milestone.user_id == user_id).first()
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        milestone.is_completed = not milestone.is_completed
        milestone.completed_at = datetime.utcnow() if milestone.is_completed else None
        db.commit()

        goal = self._recalc_goal_progress(db, milestone.goal_id)
        db.refresh(milestone)
        res = MilestoneResponse.model_validate(milestone)
        res.goal_progress = goal.progress_percentage if goal else 0
        return res

goal_service = GoalService()
