from datetime import datetime, timedelta

def get_auth_token(client, email="goals_user@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Goals Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]


def test_goal_full_crud_and_progress(client):
    token = get_auth_token(client, email="goal_crud_tester@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Goal
    create_res = client.post("/api/v1/goals", headers=headers, json={
        "title": "Build Production SaaS",
        "description": "Full stack SaaS with payments",
        "category": "Programming",
        "priority": "high",
        "target_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
        "milestones": [
            {"title": "M1: Database Schema & API", "is_completed": False, "priority": "high"},
            {"title": "M2: Frontend Dashboard", "is_completed": False, "priority": "medium"}
        ]
    })
    assert create_res.status_code == 201
    goal = create_res.json()
    goal_id = goal["id"]
    assert goal["title"] == "Build Production SaaS"
    assert goal["priority"] == "high"
    assert len(goal["milestones"]) == 2
    assert goal["progress_percentage"] == 0

    # 2. View Goal
    view_res = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert view_res.status_code == 200
    assert view_res.json()["id"] == goal_id

    # 3. Add a 3rd Milestone / Goal Task
    m3_res = client.post(f"/api/v1/goals/{goal_id}/milestones", headers=headers, json={
        "title": "M3: Production Deployment",
        "priority": "urgent"
    })
    assert m3_res.status_code == 201
    m3_id = m3_res.json()["id"]

    # 4. Toggle milestone 1 and milestone 3 as completed -> 2/3 = 67%
    m1_id = goal["milestones"][0]["id"]
    t1_res = client.post(f"/api/v1/goals/milestones/{m1_id}/toggle", headers=headers)
    assert t1_res.status_code == 200
    assert t1_res.json()["is_completed"] is True
    assert round(t1_res.json()["goal_progress"]) == 33

    t3_res = client.post(f"/api/v1/goals/milestones/{m3_id}/toggle", headers=headers)
    assert t3_res.status_code == 200
    assert round(t3_res.json()["goal_progress"]) == 67

    # Check goal itself has 67%
    g_check = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert g_check.status_code == 200
    assert round(g_check.json()["progress_percentage"]) == 67

    # 5. Edit Goal
    update_res = client.put(f"/api/v1/goals/{goal_id}", headers=headers, json={
        "title": "Build Scalable SaaS Enterprise",
        "priority": "urgent"
    })
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Build Scalable SaaS Enterprise"
    assert update_res.json()["priority"] == "urgent"

    # 6. Delete milestone
    del_m_res = client.delete(f"/api/v1/goals/milestones/{m3_id}", headers=headers)
    assert del_m_res.status_code in (200, 204)
    g_check2 = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert g_check2.json()["progress_percentage"] == 50  # 1 of 2 remaining completed = 50%

    # 7. Delete Goal
    del_res = client.delete(f"/api/v1/goals/{goal_id}", headers=headers)
    assert del_res.status_code in (200, 204)

    # 8. Verify Goal is gone
    check_res = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert check_res.status_code == 404
