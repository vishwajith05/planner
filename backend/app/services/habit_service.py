from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date
import uuid

from backend.app.models.habit import Habit, HabitCompletion
from backend.app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitToggleResponse, HabitStatsResponse

class HabitService:
    def get_habits(self, db: Session, user_id: str, include_archived: bool = False) -> List[HabitResponse]:
        query = db.query(Habit).filter(Habit.user_id == user_id)
        if not include_archived:
            query = query.filter(Habit.is_archived == False)
        habits = query.order_by(Habit.created_at.desc()).all()

        today_str = date.today().isoformat()
        today_completions = {
            c.habit_id for c in db.query(HabitCompletion).filter(
                HabitCompletion.user_id == user_id,
                HabitCompletion.completion_date == today_str
            ).all()
        }

        result = []
        for h in habits:
            resp = HabitResponse.model_validate(h)
            resp.is_completed_today = h.id in today_completions
            result.append(resp)
        return result

    def create_habit(self, db: Session, user_id: str, habit_in: HabitCreate) -> Habit:
        habit = Habit(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=habit_in.title,
            description=habit_in.description,
            category=habit_in.category or "Health",
            frequency=habit_in.frequency,
            target_days_per_week=habit_in.target_days_per_week,
            streak_count=0,
            best_streak=0
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    def toggle_habit_today(self, db: Session, user_id: str, habit_id: str, for_date: Optional[str] = None) -> HabitToggleResponse:
        habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
        if not habit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

        target_date_str = for_date or date.today().isoformat()

        existing = db.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date == target_date_str
        ).first()

        if existing:
            # Uncomplete
            db.delete(existing)
            habit.streak_count = max(0, habit.streak_count - 1)
            is_completed = False
        else:
            # Complete
            new_comp = HabitCompletion(
                id=str(uuid.uuid4()),
                habit_id=habit_id,
                user_id=user_id,
                completion_date=target_date_str
            )
            db.add(new_comp)
            habit.streak_count += 1
            if habit.streak_count > habit.best_streak:
                habit.best_streak = habit.streak_count
            is_completed = True

        db.commit()
        db.refresh(habit)

        return HabitToggleResponse(
            habit_id=habit_id,
            date=target_date_str,
            is_completed=is_completed,
            current_streak=habit.streak_count,
            best_streak=habit.best_streak
        )

    def get_habit_stats(self, db: Session, user_id: str) -> HabitStatsResponse:
        habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.is_archived == False).all()
        today_str = date.today().isoformat()
        completions_today = db.query(HabitCompletion).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date == today_str
        ).count()

        total = len(habits)
        rate = (completions_today / total * 100.0) if total > 0 else 0.0
        longest = max([h.best_streak for h in habits], default=0)

        return HabitStatsResponse(
            total_active_habits=total,
            completed_today_count=completions_today,
            daily_completion_rate=round(rate, 1),
            longest_active_streak=longest
        )

    def update_habit(self, db: Session, user_id: str, habit_id: str, habit_in) -> Habit:
        habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
        if not habit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        update_data = habit_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(habit, field, value)
        db.commit()
        db.refresh(habit)
        return habit

    def delete_habit(self, db: Session, user_id: str, habit_id: str) -> None:
        habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
        if not habit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        # Delete completions first
        db.query(HabitCompletion).filter(HabitCompletion.habit_id == habit_id).delete()
        db.delete(habit)
        db.commit()

habit_service = HabitService()
