from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from backend.app.models.goal import Goal, Milestone
from backend.app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, MilestoneCreate, MilestoneResponse

class GoalService:
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

    def toggle_milestone(self, db: Session, user_id: str, milestone_id: str) -> MilestoneResponse:
        milestone = db.query(Milestone).filter(Milestone.id == milestone_id, Milestone.user_id == user_id).first()
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        milestone.is_completed = not milestone.is_completed
        milestone.completed_at = datetime.utcnow() if milestone.is_completed else None
        db.commit()

        # Recalculate goal progress
        all_milestones = db.query(Milestone).filter(Milestone.goal_id == milestone.goal_id).all()
        if all_milestones:
            completed_count = sum(1 for m in all_milestones if m.is_completed)
            progress = (completed_count / len(all_milestones)) * 100.0
            goal = db.query(Goal).filter(Goal.id == milestone.goal_id).first()
            if goal:
                goal.progress_percentage = round(progress, 1)
                if progress >= 100.0:
                    goal.status = "completed"
                elif goal.status == "completed":
                    goal.status = "in_progress"
                db.commit()

        db.refresh(milestone)
        return MilestoneResponse.model_validate(milestone)

    def delete_goal(self, db: Session, user_id: str, goal_id: str) -> None:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        db.query(Milestone).filter(Milestone.goal_id == goal_id).delete()
        db.delete(goal)
        db.commit()

goal_service = GoalService()
