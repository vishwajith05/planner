from datetime import datetime, timedelta
from backend.app.ai.scheduling.anti_boredom import interleave_tasks_anti_boredom

def get_auth_token(client, email="ai_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "AI Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]


def test_ai_quick_add_nl_parsing(client):
    token = get_auth_token(client, email="quickadd@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    prompt = "Study Python algorithms tomorrow at 6 AM for 2 hours urgent"
    res = client.post("/api/v1/ai/parse-task", headers=headers, json={"prompt": prompt})
    assert res.status_code == 200
    data = res.json()

    assert data["category"] == "Programming"
    assert data["priority"] == "urgent"
    assert data["estimated_minutes"] == 120
    assert "suggested_due_date" in data
    assert data["confidence"] > 0.8


def test_ai_daily_scheduling_engine(client):
    token = get_auth_token(client, email="scheduler@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 pending tasks
    for i, (title, cat, dur, prio) in enumerate([
        ("Code Review", "Programming", 60, "urgent"),
        ("Read Security Whitepaper", "Cybersecurity", 90, "high"),
        ("Send Status Email", "Work", 30, "low"),
    ]):
        client.post("/api/v1/tasks", headers=headers, json={
            "title": title,
            "category": cat,
            "estimated_minutes": dur,
            "priority": prio,
            "is_completed": False
        })

    # Add a fixed calendar commitment (e.g. 10:00 - 11:00 AM)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Mandatory Team Standup",
        "start_time": f"{today_str}T10:00:00",
        "end_time": f"{today_str}T11:00:00",
        "is_fixed": True
    })

    # Request AI daily schedule
    res = client.post("/api/v1/ai/daily-schedule", headers=headers, json={
        "date": today_str,
        "day_start_hour": 8,
        "day_end_hour": 18
    })
    assert res.status_code == 200
    schedule = res.json()

    assert schedule["date"] == today_str
    assert len(schedule["scheduled"]) >= 3
    assert schedule["total_work_minutes"] == 180

    # Verify no scheduled task overlaps with 10:00 - 11:00 fixed event
    for slot in schedule["scheduled"]:
        start_dt = datetime.fromisoformat(slot["start"])
        end_dt = datetime.fromisoformat(slot["end"])
        fixed_start = datetime.fromisoformat(f"{today_str}T10:00:00")
        fixed_end = datetime.fromisoformat(f"{today_str}T11:00:00")
        assert not (start_dt < fixed_end and end_dt > fixed_start), (
            f"Task {slot['title']} overlaps with fixed standup!"
        )


def test_ai_weekly_plan_and_workload(client):
    token = get_auth_token(client, email="weekly@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Create tasks
    for i in range(5):
        client.post("/api/v1/tasks", headers=headers, json={
            "title": f"Sprint Item #{i+1}",
            "category": "Work",
            "estimated_minutes": 60,
            "priority": "medium",
            "is_completed": False
        })

    # Weekly plan
    res = client.post("/api/v1/ai/weekly-plan", headers=headers, json={
        "day_start_hour": 8,
        "day_end_hour": 18,
        "rest_days": [6], # Sunday rest
        "max_minutes_per_day": 480
    })
    assert res.status_code == 200
    plan = res.json()
    assert len(plan["day_plans"]) == 7
    # Sunday should be marked rest day
    assert plan["day_plans"][6]["is_rest_day"] is True

    # Workload analysis
    analysis_res = client.get("/api/v1/ai/workload-analysis", headers=headers)
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()
    assert analysis["total_pending_minutes"] >= 300
    assert "recommendations" in analysis


def test_ai_rescheduling_of_overdue(client):
    token = get_auth_token(client, email="reschedule@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Create an overdue task
    past = (datetime.utcnow() - timedelta(days=2)).isoformat()
    client.post("/api/v1/tasks", headers=headers, json={
        "title": "Unfinished Database Migration",
        "category": "Programming",
        "priority": "high",
        "estimated_minutes": 60,
        "due_date": past,
        "is_completed": False
    })

    res = client.post("/api/v1/ai/reschedule", headers=headers, json={"days_ahead": 3})
    assert res.status_code == 200
    data = res.json()
    assert len(data["suggestions"]) >= 1
    assert data["suggestions"][0]["title"] == "Unfinished Database Migration"
    assert "suggested_start" in data["suggestions"][0]


def test_anti_boredom_cognitive_interleaving():
    tasks = [
        {"title": "Task 1", "category": "Programming", "priority": "high"},
        {"title": "Task 2", "category": "Programming", "priority": "high"},
        {"title": "Task 3", "category": "Health", "priority": "high"},
        {"title": "Task 4", "category": "Work", "priority": "high"},
    ]
    interleaved = interleave_tasks_anti_boredom(tasks)
    assert len(interleaved) == 4
    # The two programming tasks should not be strictly adjacent if an alternate exists
    types = [t["category"] for t in interleaved]
    assert not (types[0] == "Programming" and types[1] == "Programming")
