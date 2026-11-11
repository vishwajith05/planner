from datetime import datetime, timedelta, date

def get_auth_token(client, email="productivity_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Productivity Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]

def test_habit_lifecycle_and_streaks(client):
    token = get_auth_token(client, email="habits@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create habit
    create_res = client.post("/api/v1/habits", headers=headers, json={
        "title": "Daily LeetCode Problem",
        "description": "Solve 1 algorithm problem every morning",
        "category": "Programming",
        "frequency": "daily",
        "target_days_per_week": 7
    })
    assert create_res.status_code == 201
    habit_id = create_res.json()["id"]
    assert create_res.json()["streak_count"] == 0

    # 2. Toggle habit today (complete)
    toggle_res = client.post(f"/api/v1/habits/{habit_id}/toggle", headers=headers)
    assert toggle_res.status_code == 200
    t_data = toggle_res.json()
    assert t_data["is_completed"] is True
    assert t_data["current_streak"] == 1
    assert t_data["best_streak"] == 1

    # 3. Check habit stats
    stats_res = client.get("/api/v1/habits/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_active_habits"] == 1
    assert stats["completed_today_count"] == 1
    assert stats["daily_completion_rate"] == 100.0

    # 4. Toggle habit back (uncomplete)
    untoggle_res = client.post(f"/api/v1/habits/{habit_id}/toggle", headers=headers)
    assert untoggle_res.status_code == 200
    assert untoggle_res.json()["is_completed"] is False
    assert untoggle_res.json()["current_streak"] == 0

def test_focus_pomodoro_sessions(client):
    token = get_auth_token(client, email="focus@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Record 25-minute focus session
    res = client.post("/api/v1/focus/sessions", headers=headers, json={
        "duration_minutes": 25,
        "session_type": "focus",
        "completed": True,
        "notes": "Studied graph algorithms"
    })
    assert res.status_code == 201
    assert res.json()["duration_minutes"] == 25

    # Record 5-minute break
    client.post("/api/v1/focus/sessions", headers=headers, json={
        "duration_minutes": 5,
        "session_type": "short_break",
        "completed": True
    })

    # Check stats
    stats_res = client.get("/api/v1/focus/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_focus_minutes_today"] == 25
    assert stats["total_sessions_today"] >= 2

def test_goals_and_milestones_progression(client):
    token = get_auth_token(client, email="goals@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Goal with 2 milestones
    goal_payload = {
        "title": "Become a Cybersecurity Specialist",
        "description": "Master network protocols, penetration testing, and security compliance",
        "category": "Cybersecurity",
        "milestones": [
            {"title": "CompTIA Security+ Certification", "is_completed": False, "order_index": 0},
            {"title": "Build Home Lab & Exploit Vulnerabilities", "is_completed": False, "order_index": 1}
        ]
    }
    create_res = client.post("/api/v1/goals", headers=headers, json=goal_payload)
    assert create_res.status_code == 201
    goal = create_res.json()
    assert goal["progress_percentage"] == 0.0
    assert len(goal["milestones"]) == 2
    m1_id = goal["milestones"][0]["id"]
    m2_id = goal["milestones"][1]["id"]

    # 2. Complete Milestone 1 -> progress should become 50%
    m1_toggle = client.post(f"/api/v1/goals/milestones/{m1_id}/toggle", headers=headers)
    assert m1_toggle.status_code == 200
    assert m1_toggle.json()["is_completed"] is True

    goals_list = client.get("/api/v1/goals", headers=headers).json()
    assert goals_list[0]["progress_percentage"] == 50.0
    assert goals_list[0]["status"] == "in_progress"

    # 3. Complete Milestone 2 -> progress should reach 100% and goal status become 'completed'
    m2_toggle = client.post(f"/api/v1/goals/milestones/{m2_id}/toggle", headers=headers)
    assert m2_toggle.status_code == 200

    goals_list2 = client.get("/api/v1/goals", headers=headers).json()
    assert goals_list2[0]["progress_percentage"] == 100.0
    assert goals_list2[0]["status"] == "completed"
