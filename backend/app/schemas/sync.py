from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SyncMutation(BaseModel):
    id: str  # Unique operation ID
    entity_type: str  # 'task', 'habit', 'focus', 'goal'
    action: str  # 'create', 'update', 'delete', 'toggle'
    entity_id: str
    data: Optional[Dict[str, Any]] = None
    client_timestamp: datetime = Field(default_factory=datetime.utcnow)


class MutationResult(BaseModel):
    mutation_id: str
    entity_type: str
    entity_id: str
    status: str  # 'applied', 'conflict_server_wins', 'error'
    message: Optional[str] = None


class SyncPushRequest(BaseModel):
    mutations: List[SyncMutation]


class SyncPushResponse(BaseModel):
    applied_count: int
    conflict_count: int
    results: List[MutationResult]
    server_timestamp: datetime


class SyncPullResponse(BaseModel):
    server_timestamp: datetime
    tasks: List[Dict[str, Any]]
    habits: List[Dict[str, Any]]
    focus_sessions: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]


class FullSyncRequest(BaseModel):
    last_synced_at: Optional[datetime] = None
    mutations: List[SyncMutation] = []


class FullSyncResponse(BaseModel):
    push_results: SyncPushResponse
    pull_data: SyncPullResponse
