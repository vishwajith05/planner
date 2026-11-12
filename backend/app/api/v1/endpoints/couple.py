from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.couple_service import couple_service
from backend.app.schemas.couple import (
    CoupleInviteAccept, SharedGoalCreate, SharedGoalProgressUpdate,
    SharedHabitCreate, CheckInCreate, CoupleChallengeCreate, CoupleChallengeProgressUpdate
)

router = APIRouter()

# ── Couple Pairing ──────────────────────────────────────────────────────────

@router.post("/invite", status_code=status.HTTP_201_CREATED, summary="Create a partner invite code")
def create_invite(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.create_invite(db, current_user.id)

@router.post("/accept", summary="Accept a partner invite")
def accept_invite(
    payload: CoupleInviteAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.accept_invite(db, current_user.id, payload)

@router.get("/", summary="Get current couple relationship")
def get_my_couple(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = couple_service.get_my_couple(db, current_user.id)
    if not result:
        return {"status": "none", "message": "No active couple relationship"}
    return result

@router.delete("/unpair", status_code=status.HTTP_204_NO_CONTENT, summary="End couple relationship")
def unpair(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    couple_service.unpair(db, current_user.id)

# ── Shared Goals ────────────────────────────────────────────────────────────

@router.post("/goals", status_code=status.HTTP_201_CREATED, summary="Create a shared goal")
def create_goal(
    goal_in: SharedGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.create_shared_goal(db, current_user.id, goal_in)

@router.get("/goals", summary="Get all shared goals")
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.get_shared_goals(db, current_user.id)

@router.put("/goals/{goal_id}/progress", summary="Update my progress on a shared goal")
def update_goal_progress(
    goal_id: str,
    update: SharedGoalProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.update_goal_progress(db, current_user.id, goal_id, update)

# ── Shared Habits ───────────────────────────────────────────────────────────

@router.post("/habits", status_code=status.HTTP_201_CREATED, summary="Create a shared habit")
def create_habit(
    habit_in: SharedHabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.create_shared_habit(db, current_user.id, habit_in)

@router.get("/habits", summary="Get all shared habits")
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.get_shared_habits(db, current_user.id)

@router.put("/habits/{habit_id}/toggle", summary="Toggle today's shared habit completion")
def toggle_habit(
    habit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.toggle_shared_habit(db, current_user.id, habit_id)

# ── Check-ins ───────────────────────────────────────────────────────────────

@router.post("/checkins", status_code=status.HTTP_201_CREATED, summary="Submit daily check-in")
def submit_checkin(
    check_in: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.submit_check_in(db, current_user.id, check_in)

@router.get("/checkins", summary="Get couple check-ins history")
def get_checkins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.get_check_ins(db, current_user.id)

# ── Couple Challenges ───────────────────────────────────────────────────────

@router.post("/challenges", status_code=status.HTTP_201_CREATED, summary="Create a couple challenge")
def create_challenge(
    ch_in: CoupleChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.create_challenge(db, current_user.id, ch_in)

@router.get("/challenges", summary="Get couple challenges")
def get_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.get_challenges(db, current_user.id)

@router.put("/challenges/{challenge_id}/progress", summary="Update challenge progress")
def update_challenge_progress(
    challenge_id: str,
    update: CoupleChallengeProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.update_challenge_progress(db, current_user.id, challenge_id, update)

# ── AI Suggestions ──────────────────────────────────────────────────────────

@router.get("/ai-suggestions", summary="Get AI-powered growth suggestions for the couple")
def get_ai_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return couple_service.get_ai_suggestions(db, current_user.id)
