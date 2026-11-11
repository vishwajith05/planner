from datetime import datetime, timedelta

def get_auth_token(client, email="calendar_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Calendar Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]

def test_calendar_and_conflict_detection(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    slot1_start = now + timedelta(hours=2)
    slot1_end = slot1_start + timedelta(hours=2)

    # 1. Schedule a fixed commitment (e.g., University lecture / Team Standup)
    fixed_res = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Computer Networks Lecture",
        "description": "Fixed academic commitment",
        "start_time": slot1_start.isoformat(),
        "end_time": slot1_end.isoformat(),
        "is_fixed": True,
        "category": "Education"
    })
    assert fixed_res.status_code == 201
    event_id = fixed_res.json()["id"]

    # 2. Check for conflicts with an overlapping time-slot
    overlap_start = slot1_start + timedelta(minutes=30)
    overlap_end = slot1_end + timedelta(minutes=30)
    conflict_check = client.post("/api/v1/calendar/check-conflicts", headers=headers, json={
        "start_time": overlap_start.isoformat(),
        "end_time": overlap_end.isoformat()
    })
    assert conflict_check.status_code == 200
    res_data = conflict_check.json()
    assert res_data["has_conflict"] is True
    assert len(res_data["conflicts"]) == 1
    assert res_data["conflicts"][0]["existing_event_id"] == event_id
    assert res_data["conflicts"][0]["is_fixed"] is True
    assert "Fixed commitment clash" in res_data["conflicts"][0]["conflict_reason"]

    # 3. Check for conflict with a non-overlapping time-slot (free slot)
    free_start = slot1_end + timedelta(hours=1)
    free_end = free_start + timedelta(hours=1)
    free_check = client.post("/api/v1/calendar/check-conflicts", headers=headers, json={
        "start_time": free_start.isoformat(),
        "end_time": free_end.isoformat()
    })
    assert free_check.status_code == 200
    assert free_check.json()["has_conflict"] is False

    # 4. List events
    events_res = client.get("/api/v1/calendar/events", headers=headers)
    assert events_res.status_code == 200
    assert len(events_res.json()) >= 1

    # 5. Delete event
    del_res = client.delete(f"/api/v1/calendar/events/{event_id}", headers=headers)
    assert del_res.status_code == 204
