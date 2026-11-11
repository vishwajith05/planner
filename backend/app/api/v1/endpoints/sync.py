from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.app.database.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.services.sync_service import sync_service
from backend.app.schemas.sync import (
    SyncPushRequest,
    SyncPushResponse,
    SyncPullResponse,
    FullSyncRequest,
    FullSyncResponse,
)

router = APIRouter()


@router.post("/push", response_model=SyncPushResponse, status_code=status.HTTP_200_OK)
def push_offline_mutations(
    payload: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Receives batched offline mutations (creates, updates, deletes, toggles)
    and resolves conflicts using timestamp-based Last-Write-Wins (LWW).
    """
    return sync_service.process_push(
        db=db, user_id=current_user.id, mutations=payload.mutations
    )


@router.get("/pull", response_model=SyncPullResponse, status_code=status.HTTP_200_OK)
def pull_delta_changes(
    since: Optional[datetime] = Query(None, description="ISO timestamp of last known sync"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves modified tasks, habits, focus logs, and goals since `since`.
    """
    return sync_service.process_pull(
        db=db, user_id=current_user.id, last_synced_at=since
    )


@router.post("/full", response_model=FullSyncResponse, status_code=status.HTTP_200_OK)
def full_bidirectional_sync(
    payload: FullSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atomically pushes offline queued mutations and returns server delta changes
    in a single HTTP roundtrip.
    """
    return sync_service.full_sync(
        db=db,
        user_id=current_user.id,
        mutations=payload.mutations,
        last_synced_at=payload.last_synced_at,
    )
