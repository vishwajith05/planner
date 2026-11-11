def get_token(client, email):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": email.split("@")[0]
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"]

def test_strict_user_data_isolation(client):
    token_a = get_token(client, "user_a@planwise.ai")
    token_b = get_token(client, "user_b@planwise.ai")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a confidential task
    create_res = client.post("/api/v1/tasks", headers=headers_a, json={
        "title": "User A Confidential Strategic Plan",
        "priority": "urgent",
        "category": "Entrepreneurship"
    })
    assert create_res.status_code == 201
    task_a_id = create_res.json()["id"]

    # 1. User B should NOT see Task A in their task list
    list_b = client.get("/api/v1/tasks", headers=headers_b).json()
    assert all(t["id"] != task_a_id for t in list_b)

    # 2. User B attempting to read Task A directly by ID must fail (404)
    read_b = client.get(f"/api/v1/tasks/{task_a_id}", headers=headers_b)
    assert read_b.status_code == 404

    # 3. User B attempting to update Task A must fail (404)
    update_b = client.put(f"/api/v1/tasks/{task_a_id}", headers=headers_b, json={
        "title": "Hacked Title"
    })
    assert update_b.status_code == 404

    # 4. User B attempting to toggle Task A must fail (404)
    toggle_b = client.post(f"/api/v1/tasks/{task_a_id}/toggle", headers=headers_b)
    assert toggle_b.status_code == 404

    # 5. User B attempting to delete Task A must fail (404)
    delete_b = client.delete(f"/api/v1/tasks/{task_a_id}", headers=headers_b)
    assert delete_b.status_code == 404

    # 6. Verify User A's task was unaffected by User B's unauthorized attempts
    task_a = client.get(f"/api/v1/tasks/{task_a_id}", headers=headers_a).json()
    assert task_a["title"] == "User A Confidential Strategic Plan"
