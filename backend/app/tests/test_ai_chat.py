from datetime import datetime, timedelta

def get_auth_token(client, email="chat_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Chat Assistant Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]


def test_ai_chat_assistant_flow(client):
    token = get_auth_token(client, email="chat_flow@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ask general prompt
    r1 = client.post("/api/v1/ai/assistant/chat", headers=headers, json={"message": "Hello, how can you help me?"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert "PlanWise AI" in d1["reply"]
    assert len(d1["actions"]) > 0

    # 2. Ask "What tasks are overdue?" with no overdue tasks
    r2 = client.post("/api/v1/ai/assistant/chat", headers=headers, json={"message": "What tasks are overdue?"})
    assert r2.status_code == 200
    assert "no overdue tasks" in r2.json()["reply"].lower()

    # Create an overdue task
    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    client.post("/api/v1/tasks", headers=headers, json={
        "title": "Fix Security Vulnerability CVE-2026",
        "category": "Cybersecurity",
        "priority": "urgent",
        "due_date": past,
        "is_completed": False
    })

    # 3. Ask "What tasks are overdue?" again
    r3 = client.post("/api/v1/ai/assistant/chat", headers=headers, json={"message": "Check overdue tasks"})
    assert r3.status_code == 200
    d3 = r3.json()
    assert "CVE-2026" in d3["reply"]
    assert len(d3["actions"]) > 0

    # 4. Ask "How is my productivity?"
    r4 = client.post("/api/v1/ai/assistant/chat", headers=headers, json={"message": "How is my productivity today?"})
    assert r4.status_code == 200
    d4 = r4.json()
    assert "Productivity Score" in d4["reply"]


def test_ai_goal_breakdown(client):
    token = get_auth_token(client, email="goal_breakdown@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/ai/assistant/goal-breakdown", headers=headers, json={
        "goal_title": "Become a Senior Flutter & Python Developer",
        "category": "Education"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["goal_title"] == "Become a Senior Flutter & Python Developer"
    assert len(data["milestones"]) >= 3
    assert data["estimated_total_days"] > 0
    assert len(data["recommendations"]) > 0


def test_ai_productivity_coach_insights(client):
    token = get_auth_token(client, email="coach_tester@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Seed 1 completed task and 1 focus session
    client.post("/api/v1/tasks", headers=headers, json={
        "title": "Completed Architecture Plan",
        "category": "Programming",
        "is_completed": True
    })
    client.post("/api/v1/focus/sessions", headers=headers, json={
        "duration_minutes": 50,
        "session_type": "focus",
        "completed": True
    })

    res = client.get("/api/v1/ai/assistant/productivity-insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert insights["overall_score"] >= 50
    assert len(insights["insights"]) >= 3
    assert "summary" in insights
