from datetime import datetime, timedelta

def get_auth_token(client, email="sync_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Sync Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]


def test_offline_push_task_creation(client):
    token = get_auth_token(client, email="push_test@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    mutations = [
        {
            "id": "mut-1",
            "entity_type": "task",
            "action": "create",
            "entity_id": "offline-task-101",
            "data": {
                "title": "Offline Created Task",
                "category": "Programming",
                "priority": "high",
                "estimated_minutes": 45
            },
            "client_timestamp": datetime.utcnow().isoformat()
        }
    ]

    res = client.post("/api/v1/sync/push", headers=headers, json={"mutations": mutations})
    assert res.status_code == 200
    data = res.json()
    assert data["applied_count"] == 1
    assert data["conflict_count"] == 0
    assert data["results"][0]["status"] == "applied"

    # Verify task was created on server
    task_res = client.get("/api/v1/tasks/offline-task-101", headers=headers)
    assert task_res.status_code == 200
    assert task_res.json()["title"] == "Offline Created Task"


def test_sync_conflict_resolution_lww(client):
    token = get_auth_token(client, email="conflict_test@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a task on server
    task_res = client.post("/api/v1/tasks", headers=headers, json={
        "title": "Server Authoritative Task",
        "category": "Work",
        "priority": "low"
    })
    task_id = task_res.json()["id"]

    # 2. Modify task on server so server updated_at is recent
    client.put(f"/api/v1/tasks/{task_id}", headers=headers, json={
        "title": "Server Updated Title"
    })

    # 3. Simulate an offline client with an OLD stale mutation timestamp trying to overwrite
    old_timestamp = (datetime.utcnow() - timedelta(hours=2)).isoformat()
    stale_mutation = [
        {
            "id": "mut-stale-1",
            "entity_type": "task",
            "action": "update",
            "entity_id": task_id,
            "data": {"title": "Stale Client Title"},
            "client_timestamp": old_timestamp
        }
    ]

    push_res = client.post("/api/v1/sync/push", headers=headers, json={"mutations": stale_mutation})
    assert push_res.status_code == 200
    push_data = push_res.json()
    # Conflict detected: server wins!
    assert push_data["conflict_count"] == 1
    assert push_data["results"][0]["status"] == "conflict_server_wins"

    # Verify server title remains unchanged
    check = client.get(f"/api/v1/tasks/{task_id}", headers=headers).json()
    assert check["title"] == "Server Updated Title"


def test_full_bidirectional_sync(client):
    token = get_auth_token(client, email="fullsync@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    mutations = [
        {
            "id": "mut-full-1",
            "entity_type": "focus",
            "action": "create",
            "entity_id": "focus-offline-1",
            "data": {
                "duration_minutes": 25,
                "session_type": "focus",
                "completed": True,
                "notes": "Offline deep work"
            },
            "client_timestamp": datetime.utcnow().isoformat()
        }
    ]

    res = client.post("/api/v1/sync/full", headers=headers, json={
        "mutations": mutations,
        "last_synced_at": None
    })
    assert res.status_code == 200
    data = res.json()
    assert data["push_results"]["applied_count"] == 1
    assert len(data["pull_data"]["focus_sessions"]) >= 1
