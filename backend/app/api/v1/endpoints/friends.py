from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.friend_service import friend_service
from backend.app.schemas.friendship import (
    FriendRequest, ChallengeCreate, ChallengeProgressUpdate,
    EncouragementCreate, FocusSessionCreate
)

router = APIRouter()

# ── Friend Discovery & Requests ─────────────────────────────────────────────

@router.get("/search", summary="Search users by name or email")
def search_users(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.search_users(db, q, current_user.id)

@router.post("/request", status_code=status.HTTP_201_CREATED, summary="Send a friend request")
def send_request(
    req: FriendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.send_friend_request(db, current_user.id, req)

@router.get("/requests/pending", summary="Get incoming pending friend requests")
def get_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.get_pending_requests(db, current_user.id)

@router.put("/request/{friendship_id}/{action}", summary="Accept or reject a friend request")
def respond_request(
    friendship_id: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.respond_to_request(db, current_user.id, friendship_id, action)

@router.get("/", summary="Get all accepted friends")
def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.get_friends(db, current_user.id)

@router.delete("/{friendship_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a friend")
def remove_friend(
    friendship_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friend_service.remove_friend(db, current_user.id, friendship_id)

# ── Shared Challenges ───────────────────────────────────────────────────────

@router.post("/challenges", status_code=status.HTTP_201_CREATED, summary="Create a shared challenge")
def create_challenge(
    challenge_in: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.create_challenge(db, current_user.id, challenge_in)

@router.get("/challenges", summary="Get my challenges")
def get_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.get_challenges(db, current_user.id)

@router.put("/challenges/{challenge_id}/progress", summary="Update my progress in a challenge")
def update_progress(
    challenge_id: str,
    update: ChallengeProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.update_challenge_progress(db, current_user.id, challenge_id, update)

# ── Encouragement Messages ──────────────────────────────────────────────────

@router.post("/encourage", status_code=status.HTTP_201_CREATED, summary="Send encouragement message")
def send_encouragement(
    msg_in: EncouragementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.send_encouragement(db, current_user.id, msg_in)

@router.get("/messages", summary="Get encouragement messages received")
def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.get_messages(db, current_user.id)

@router.put("/messages/{message_id}/read", summary="Mark message as read")
def mark_read(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friend_service.mark_message_read(db, current_user.id, message_id)
    return {"message": "Marked as read"}

# ── Focus Together ──────────────────────────────────────────────────────────

@router.post("/focus", status_code=status.HTTP_201_CREATED, summary="Create a focus-together session")
def create_focus(
    session_in: FocusSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.create_focus_session(db, current_user.id, session_in)

@router.post("/focus/join/{session_code}", summary="Join a focus session by code")
def join_focus(
    session_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.join_focus_session(db, current_user.id, session_code)

# ── Activity Feed ───────────────────────────────────────────────────────────

@router.get("/feed", summary="Get friends' public activity feed")
def get_activity_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return friend_service.get_activity_feed(db, current_user.id)
