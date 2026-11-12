from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date
import uuid
import secrets

from backend.app.models.couple import (
    CoupleRelationship, SharedGoal, SharedHabit, SharedHabitCompletion,
    CoupleCheckIn, CoupleChallenge
)
from backend.app.models.user import User
from backend.app.schemas.couple import (
    CoupleInviteAccept, SharedGoalCreate, SharedGoalProgressUpdate,
    SharedHabitCreate, CheckInCreate, CoupleChallengeCreate, CoupleChallengeProgressUpdate
)


class CoupleService:

    # ── Couple Pairing ──────────────────────────────────────────────────────

    def create_invite(self, db: Session, user_id: str) -> CoupleRelationship:
        """Create an invite code for pairing. Checks for existing active relationship."""
        existing = db.query(CoupleRelationship).filter(
            or_(
                CoupleRelationship.partner_a_id == user_id,
                CoupleRelationship.partner_b_id == user_id
            ),
            CoupleRelationship.status == "active"
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="You already have an active couple relationship")

        # Revoke any pending invites
        old_pending = db.query(CoupleRelationship).filter(
            CoupleRelationship.partner_a_id == user_id,
            CoupleRelationship.status == "pending"
        ).all()
        for old in old_pending:
            db.delete(old)

        invite_code = secrets.token_urlsafe(8).upper()[:10]
        while db.query(CoupleRelationship).filter(CoupleRelationship.invite_code == invite_code).first():
            invite_code = secrets.token_urlsafe(8).upper()[:10]

        couple = CoupleRelationship(
            id=str(uuid.uuid4()),
            partner_a_id=user_id,
            partner_b_id="",
            invite_code=invite_code,
            status="pending"
        )
        db.add(couple)
        db.commit()
        db.refresh(couple)
        return couple

    def accept_invite(self, db: Session, user_id: str, payload: CoupleInviteAccept) -> CoupleRelationship:
        """Accept a partner invite using the invite code."""
        couple = db.query(CoupleRelationship).filter(
            CoupleRelationship.invite_code == payload.invite_code.upper(),
            CoupleRelationship.status == "pending"
        ).first()
        if not couple:
            raise HTTPException(status_code=404, detail="Invalid or expired invite code")
        if couple.partner_a_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot accept your own invite")

        # Ensure user doesn't already have an active relationship
        existing = db.query(CoupleRelationship).filter(
            or_(
                CoupleRelationship.partner_a_id == user_id,
                CoupleRelationship.partner_b_id == user_id
            ),
            CoupleRelationship.status == "active"
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="You already have an active couple relationship")

        couple.partner_b_id = user_id
        couple.status = "active"
        couple.activated_at = datetime.utcnow()
        db.commit()
        db.refresh(couple)
        return couple

    def get_my_couple(self, db: Session, user_id: str) -> Optional[dict]:
        """Get the current user's couple relationship with partner details."""
        couple = db.query(CoupleRelationship).filter(
            or_(
                CoupleRelationship.partner_a_id == user_id,
                CoupleRelationship.partner_b_id == user_id
            ),
            CoupleRelationship.status.in_(["active", "pending"])
        ).first()
        if not couple:
            return None

        result = {
            "id": couple.id,
            "invite_code": couple.invite_code,
            "status": couple.status,
            "created_at": couple.created_at.isoformat(),
            "activated_at": couple.activated_at.isoformat() if couple.activated_at else None,
            "partner_a_id": couple.partner_a_id,
            "partner_b_id": couple.partner_b_id,
            "is_partner_a": couple.partner_a_id == user_id
        }

        pa = db.query(User).filter(User.id == couple.partner_a_id).first()
        result["partner_a"] = {"id": pa.id, "name": pa.full_name or pa.email, "email": pa.email} if pa else None

        if couple.partner_b_id:
            pb = db.query(User).filter(User.id == couple.partner_b_id).first()
            result["partner_b"] = {"id": pb.id, "name": pb.full_name or pb.email, "email": pb.email} if pb else None
        else:
            result["partner_b"] = None

        return result

    def unpair(self, db: Session, user_id: str) -> None:
        """End the couple relationship."""
        couple = db.query(CoupleRelationship).filter(
            or_(
                CoupleRelationship.partner_a_id == user_id,
                CoupleRelationship.partner_b_id == user_id
            ),
            CoupleRelationship.status.in_(["active", "pending"])
        ).first()
        if not couple:
            raise HTTPException(status_code=404, detail="No active relationship found")
        couple.status = "ended"
        couple.ended_at = datetime.utcnow()
        db.commit()

    def _get_couple_or_403(self, db: Session, user_id: str) -> CoupleRelationship:
        """Get the couple relationship, raising 403 if user is not in one."""
        couple = db.query(CoupleRelationship).filter(
            or_(
                CoupleRelationship.partner_a_id == user_id,
                CoupleRelationship.partner_b_id == user_id
            ),
            CoupleRelationship.status == "active"
        ).first()
        if not couple:
            raise HTTPException(status_code=403, detail="You must be in an active couple relationship")
        return couple

    # ── Shared Goals ────────────────────────────────────────────────────────

    def create_shared_goal(self, db: Session, user_id: str, goal_in: SharedGoalCreate) -> SharedGoal:
        couple = self._get_couple_or_403(db, user_id)
        goal = SharedGoal(
            id=str(uuid.uuid4()),
            couple_id=couple.id,
            creator_id=user_id,
            title=goal_in.title,
            description=goal_in.description,
            category=goal_in.category,
            target_date=goal_in.target_date,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def get_shared_goals(self, db: Session, user_id: str) -> List[dict]:
        couple = self._get_couple_or_403(db, user_id)
        goals = db.query(SharedGoal).filter(SharedGoal.couple_id == couple.id).all()
        is_a = couple.partner_a_id == user_id
        return [self._goal_to_dict(g, is_a) for g in goals]

    def _goal_to_dict(self, g: SharedGoal, is_a: bool) -> dict:
        combined = round((g.partner_a_progress + g.partner_b_progress) / 2)
        return {
            "id": g.id,
            "couple_id": g.couple_id,
            "creator_id": g.creator_id,
            "title": g.title,
            "description": g.description,
            "category": g.category,
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "partner_a_progress": g.partner_a_progress,
            "partner_b_progress": g.partner_b_progress,
            "my_progress": g.partner_a_progress if is_a else g.partner_b_progress,
            "combined_progress": combined,
            "is_completed": g.is_completed,
            "created_at": g.created_at.isoformat()
        }

    def update_goal_progress(self, db: Session, user_id: str, goal_id: str, update: SharedGoalProgressUpdate) -> dict:
        couple = self._get_couple_or_403(db, user_id)
        goal = db.query(SharedGoal).filter(SharedGoal.id == goal_id, SharedGoal.couple_id == couple.id).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Shared goal not found")

        is_a = couple.partner_a_id == user_id
        if is_a:
            goal.partner_a_progress = update.progress
        else:
            goal.partner_b_progress = update.progress

        if goal.partner_a_progress >= 100 and goal.partner_b_progress >= 100:
            goal.is_completed = True

        db.commit()
        is_a_flag = couple.partner_a_id == user_id
        return self._goal_to_dict(goal, is_a_flag)

    # ── Shared Habits ───────────────────────────────────────────────────────

    def create_shared_habit(self, db: Session, user_id: str, habit_in: SharedHabitCreate) -> SharedHabit:
        couple = self._get_couple_or_403(db, user_id)
        habit = SharedHabit(
            id=str(uuid.uuid4()),
            couple_id=couple.id,
            creator_id=user_id,
            title=habit_in.title,
            description=habit_in.description,
            frequency=habit_in.frequency
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    def get_shared_habits(self, db: Session, user_id: str) -> List[dict]:
        couple = self._get_couple_or_403(db, user_id)
        habits = db.query(SharedHabit).filter(
            SharedHabit.couple_id == couple.id,
            SharedHabit.is_active == True
        ).all()
        today = date.today().isoformat()
        is_a = couple.partner_a_id == user_id
        result = []
        for h in habits:
            a_done = db.query(SharedHabitCompletion).filter(
                SharedHabitCompletion.habit_id == h.id,
                SharedHabitCompletion.user_id == couple.partner_a_id,
                SharedHabitCompletion.completion_date == today
            ).first() is not None
            b_done = db.query(SharedHabitCompletion).filter(
                SharedHabitCompletion.habit_id == h.id,
                SharedHabitCompletion.user_id == couple.partner_b_id,
                SharedHabitCompletion.completion_date == today
            ).first() is not None
            result.append({
                "id": h.id,
                "couple_id": h.couple_id,
                "title": h.title,
                "description": h.description,
                "frequency": h.frequency,
                "partner_a_streak": h.partner_a_streak,
                "partner_b_streak": h.partner_b_streak,
                "my_streak": h.partner_a_streak if is_a else h.partner_b_streak,
                "today_partner_a_done": a_done,
                "today_partner_b_done": b_done,
                "today_i_done": a_done if is_a else b_done,
                "is_active": h.is_active,
                "created_at": h.created_at.isoformat()
            })
        return result

    def toggle_shared_habit(self, db: Session, user_id: str, habit_id: str) -> dict:
        couple = self._get_couple_or_403(db, user_id)
        habit = db.query(SharedHabit).filter(
            SharedHabit.id == habit_id, SharedHabit.couple_id == couple.id
        ).first()
        if not habit:
            raise HTTPException(status_code=404, detail="Shared habit not found")

        today = date.today().isoformat()
        existing = db.query(SharedHabitCompletion).filter(
            SharedHabitCompletion.habit_id == habit_id,
            SharedHabitCompletion.user_id == user_id,
            SharedHabitCompletion.completion_date == today
        ).first()

        is_a = couple.partner_a_id == user_id
        if existing:
            db.delete(existing)
            if is_a and habit.partner_a_streak > 0:
                habit.partner_a_streak -= 1
            elif not is_a and habit.partner_b_streak > 0:
                habit.partner_b_streak -= 1
            done = False
        else:
            db.add(SharedHabitCompletion(
                id=str(uuid.uuid4()),
                habit_id=habit_id,
                user_id=user_id,
                completion_date=today
            ))
            if is_a:
                habit.partner_a_streak += 1
            else:
                habit.partner_b_streak += 1
            done = True

        db.commit()
        return {"done": done, "my_streak": habit.partner_a_streak if is_a else habit.partner_b_streak}

    # ── Check-ins ───────────────────────────────────────────────────────────

    def submit_check_in(self, db: Session, user_id: str, check_in: CheckInCreate) -> CoupleCheckIn:
        couple = self._get_couple_or_403(db, user_id)
        today = date.today().isoformat()

        existing = db.query(CoupleCheckIn).filter(
            CoupleCheckIn.couple_id == couple.id,
            CoupleCheckIn.user_id == user_id,
            CoupleCheckIn.check_in_date == today
        ).first()
        if existing:
            existing.mood = check_in.mood
            existing.gratitude = check_in.gratitude
            existing.win_of_day = check_in.win_of_day
            existing.support_needed = check_in.support_needed
            db.commit()
            db.refresh(existing)
            return existing

        ci = CoupleCheckIn(
            id=str(uuid.uuid4()),
            couple_id=couple.id,
            user_id=user_id,
            mood=check_in.mood,
            gratitude=check_in.gratitude,
            win_of_day=check_in.win_of_day,
            support_needed=check_in.support_needed,
            check_in_date=today
        )
        db.add(ci)
        db.commit()
        db.refresh(ci)
        return ci

    def get_check_ins(self, db: Session, user_id: str, limit: int = 14) -> List[dict]:
        couple = self._get_couple_or_403(db, user_id)
        check_ins = db.query(CoupleCheckIn).filter(
            CoupleCheckIn.couple_id == couple.id
        ).order_by(CoupleCheckIn.check_in_date.desc()).limit(limit).all()

        result = []
        for ci in check_ins:
            u = db.query(User).filter(User.id == ci.user_id).first()
            result.append({
                "id": ci.id,
                "couple_id": ci.couple_id,
                "user_id": ci.user_id,
                "user_name": u.full_name or u.email if u else "Unknown",
                "is_me": ci.user_id == user_id,
                "mood": ci.mood,
                "gratitude": ci.gratitude,
                "win_of_day": ci.win_of_day,
                "support_needed": ci.support_needed,
                "check_in_date": ci.check_in_date,
                "created_at": ci.created_at.isoformat()
            })
        return result

    # ── Couple Challenges ───────────────────────────────────────────────────

    def create_challenge(self, db: Session, user_id: str, ch_in: CoupleChallengeCreate) -> CoupleChallenge:
        couple = self._get_couple_or_403(db, user_id)
        ch = CoupleChallenge(
            id=str(uuid.uuid4()),
            couple_id=couple.id,
            creator_id=user_id,
            title=ch_in.title,
            description=ch_in.description,
            duration_days=ch_in.duration_days,
            start_date=ch_in.start_date or datetime.utcnow(),
            is_active=True
        )
        db.add(ch)
        db.commit()
        db.refresh(ch)
        return ch

    def get_challenges(self, db: Session, user_id: str) -> List[dict]:
        couple = self._get_couple_or_403(db, user_id)
        challenges = db.query(CoupleChallenge).filter(
            CoupleChallenge.couple_id == couple.id,
            CoupleChallenge.is_active == True
        ).all()
        is_a = couple.partner_a_id == user_id
        result = []
        for c in challenges:
            combined = round((c.partner_a_progress + c.partner_b_progress) / 2)
            result.append({
                "id": c.id,
                "couple_id": c.couple_id,
                "title": c.title,
                "description": c.description,
                "duration_days": c.duration_days,
                "partner_a_progress": c.partner_a_progress,
                "partner_b_progress": c.partner_b_progress,
                "my_progress": c.partner_a_progress if is_a else c.partner_b_progress,
                "combined_progress": combined,
                "is_active": c.is_active,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "created_at": c.created_at.isoformat()
            })
        return result

    def update_challenge_progress(self, db: Session, user_id: str, ch_id: str, update: CoupleChallengeProgressUpdate) -> dict:
        couple = self._get_couple_or_403(db, user_id)
        ch = db.query(CoupleChallenge).filter(CoupleChallenge.id == ch_id, CoupleChallenge.couple_id == couple.id).first()
        if not ch:
            raise HTTPException(status_code=404, detail="Challenge not found")
        is_a = couple.partner_a_id == user_id
        if is_a:
            ch.partner_a_progress = update.progress
        else:
            ch.partner_b_progress = update.progress
        db.commit()
        combined = round((ch.partner_a_progress + ch.partner_b_progress) / 2)
        return {"progress": update.progress, "combined_progress": combined}

    def get_ai_suggestions(self, db: Session, user_id: str) -> dict:
        """AI-powered growth suggestions for the couple (uses existing AI service)."""
        couple = self._get_couple_or_403(db, user_id)
        is_a = couple.partner_a_id == user_id
        partner_id = couple.partner_b_id if is_a else couple.partner_a_id

        goals = db.query(SharedGoal).filter(SharedGoal.couple_id == couple.id).all()
        habits = db.query(SharedHabit).filter(SharedHabit.couple_id == couple.id).all()

        suggestions = [
            {
                "type": "schedule",
                "title": "Daily Learning Session",
                "description": "Schedule a shared 30-minute learning session each day at a consistent time.",
                "priority": "high"
            },
            {
                "type": "habit",
                "title": "Weekly Progress Review",
                "description": "Every Sunday, review your combined progress together and celebrate wins.",
                "priority": "medium"
            },
            {
                "type": "goal",
                "title": "Set Micro-Milestones",
                "description": f"Break your {len(goals)} shared goal(s) into weekly milestones for better momentum.",
                "priority": "high"
            },
            {
                "type": "encouragement",
                "title": "Morning Check-In",
                "description": "Start each day with a quick check-in to share your top priority for the day.",
                "priority": "medium"
            }
        ]
        return {
            "suggestions": suggestions,
            "shared_goals_count": len(goals),
            "shared_habits_count": len(habits),
            "message": "Here are personalized suggestions for your growth journey together."
        }


couple_service = CoupleService()
