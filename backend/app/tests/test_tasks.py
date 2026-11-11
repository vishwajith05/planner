def get_auth_token(client, email="taskuser@planwise.ai"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Task Tester"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]

def test_full_task_lifecycle(client):
    token = get_auth_token(client, email="lifecycle@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create task with subtasks and priority
    task_payload = {
        "title": "Build Secure JWT Authentication",
        "description": "Implement token rotation and bcrypt hashing",
        "notes": "Verify against RFC 7519",
        "priority": "urgent",
        "status": "not_started",
        "category": "Cybersecurity",
        "tags": "security,auth,fastapi",
        "estimated_minutes": 90,
        "recurrence": "none",
        "subtasks": [
            {"id": "sub-1", "title": "Bcrypt implementation", "is_completed": True},
            {"id": "sub-2", "title": "Route protection", "is_completed": False}
        ]
    }
    create_res = client.post("/api/v1/tasks", headers=headers, json=task_payload)
    assert create_res.status_code == 201
    task = create_res.json()
    task_id = task["id"]
    assert task["title"] == "Build Secure JWT Authentication"
    assert task["priority"] == "urgent"
    assert task["category"] == "Cybersecurity"
    assert len(task["subtasks"]) == 2

    # 2. Get task by ID
    get_res = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id

    # 3. Toggle completion
    toggle_res = client.post(f"/api/v1/tasks/{task_id}/toggle", headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_completed"] is True
    assert toggle_res.json()["status"] == "completed"
    assert toggle_res.json()["completed_at"] is not None

    # Toggle back
    toggle_back = client.post(f"/api/v1/tasks/{task_id}/toggle", headers=headers)
    assert toggle_back.status_code == 200
    assert toggle_back.json()["is_completed"] is False
    assert toggle_back.json()["status"] == "in_progress"

    # 4. Duplicate task
    dup_res = client.post(f"/api/v1/tasks/{task_id}/duplicate", headers=headers)
    assert dup_res.status_code == 201
    dup_task = dup_res.json()
    assert dup_task["id"] != task_id
    assert "Copy of" in dup_task["title"]
    assert dup_task["priority"] == "urgent"

    # 5. Filter tasks by category & search query
    search_res = client.get("/api/v1/tasks?category=Cybersecurity&search=JWT", headers=headers)
    assert search_res.status_code == 200
    tasks_list = search_res.json()
    assert len(tasks_list) >= 1
    assert any(t["id"] == task_id for t in tasks_list)

    # 6. Update task
    update_res = client.put(f"/api/v1/tasks/{task_id}", headers=headers, json={
        "title": "Build Secure JWT Authentication (Updated)",
        "priority": "high",
        "estimated_minutes": 120
    })
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Build Secure JWT Authentication (Updated)"
    assert update_res.json()["priority"] == "high"
    assert update_res.json()["estimated_minutes"] == 120

    # 7. Delete task
    del_res = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 204

    # Verification: should return 404 after deletion
    after_del = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert after_del.status_code == 404

def test_categories_management(client):
    token = get_auth_token(client, email="categories@planwise.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch categories
    cats_res = client.get("/api/v1/tasks/categories", headers=headers)
    assert cats_res.status_code == 200
    cats = cats_res.json()
    assert len(cats) >= 8  # 8 default categories
    cat_names = [c["name"] for c in cats]
    assert "Programming" in cat_names
    assert "Cybersecurity" in cat_names

    # Create custom category
    custom_res = client.post("/api/v1/tasks/categories", headers=headers, json={
        "name": "Robotics",
        "color": "#EF4444",
        "icon": "smart_toy"
    })
    assert custom_res.status_code == 201
    assert custom_res.json()["name"] == "Robotics"
