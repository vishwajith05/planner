from datetime import datetime, timedelta

def get_auth_token(client, email="analytics_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Analytics Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]


def test_analytics_summary_with_real_activity(client):
    token = get_auth_token(client, email="analytics_tester@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create tasks: 1 completed, 1 pending, 1 overdue
    now = datetime.utcnow()
    # Task 1 (completed, 45 min)
    t1_res = client.post("/api/v1/tasks", headers=headers, json={
        "title": "Completed Code Review",
        "category": "Programming",
        "priority": "high",
        "estimated_minutes": 45,
        "actual_minutes": 40,
        "is_completed": True
    })
    assert t1_res.status_code == 201

    # Task 2 (pending, 30 min)
    t2_res = client.post("/api/v1/tasks", headers=headers, json={
        "title": "Pending Network Configuration",
        "category": "Cybersecurity",
        "priority": "medium",
        "estimated_minutes": 30,
        "is_completed": False
    })
    assert t2_res.status_code == 201

    # Task 3 (overdue, 60 min)
    past_due = (now - timedelta(days=2)).isoformat()
    t3_res = client.post("/api/v1/tasks", headers=headers, json={
        "title": "Overdue Lab Exercise",
        "category": "Education",
        "priority": "urgent",
        "estimated_minutes": 60,
        "due_date": past_due,
        "is_completed": False
    })
    assert t3_res.status_code == 201

    # 2. Record a focus session (25 min)
    client.post("/api/v1/focus/sessions", headers=headers, json={
        "duration_minutes": 25,
        "session_type": "focus",
        "completed": True,
        "notes": "Focused work"
    })

    # 3. Create a habit & complete it
    habit_res = client.post("/api/v1/habits", headers=headers, json={
        "title": "Morning Reading",
        "category": "Education",
        "frequency": "daily"
    })
    habit_id = habit_res.json()["id"]
    client.post(f"/api/v1/habits/{habit_id}/toggle", headers=headers)

    # 4. Create a goal with 2 milestones, complete 1
    client.post("/api/v1/goals", headers=headers, json={
        "title": "Master Cloud Security",
        "category": "Cybersecurity",
        "milestones": [
            {"title": "M1: Identity & Access Management", "is_completed": True, "order_index": 0},
            {"title": "M2: VPC Peering & Firewall Audits", "is_completed": False, "order_index": 1}
        ]
    })

    # 5. Query Analytics Summary (this_week)
    analytics_res = client.get("/api/v1/analytics/summary?period=this_week", headers=headers)
    assert analytics_res.status_code == 200
    data = analytics_res.json()

    # Validate task metrics
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    assert data["pending_tasks"] == 2
    assert data["overdue_tasks"] == 1
    assert data["total_estimated_minutes"] == 135
    assert data["total_actual_minutes"] == 40
    assert data["total_focus_minutes"] >= 25

    # Validate sub-analytics
    assert data["focus"]["total_sessions"] >= 1
    assert data["focus"]["total_focus_minutes"] >= 25
    assert data["habits"]["total_habits"] == 1
    assert data["habits"]["best_streak"] >= 1
    assert data["goals"]["total_goals"] == 1
    assert data["goals"]["average_progress"] == 50.0

    # Validate category breakdown
    cats = {c["category"]: c for c in data["category_breakdown"]}
    assert "Programming" in cats
    assert cats["Programming"]["total_tasks"] == 1
    assert cats["Programming"]["completed_tasks"] == 1
    assert cats["Programming"]["completion_rate"] == 100.0


def test_analytics_period_filtering(client):
    token = get_auth_token(client, email="period_test@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    for period in ["today", "this_week", "this_month"]:
        res = client.get(f"/api/v1/analytics/summary?period={period}", headers=headers)
        assert res.status_code == 200
        summary = res.json()
        assert "period_start" in summary
        assert "period_end" in summary
        assert isinstance(summary["trends"], list)
