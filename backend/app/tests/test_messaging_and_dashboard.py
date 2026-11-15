from datetime import datetime, timedelta

def get_auth_token(client, email="social_user@planwise.ai", name="Social Tester"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": name
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return res.json()["access_token"], res.json()["user"]["id"]


def test_friend_messaging_flow(client):
    # User A and User B
    tok_a, user_a_id = get_auth_token(client, email="alice_msg@planwise.ai", name="Alice")
    tok_b, user_b_id = get_auth_token(client, email="bob_msg@planwise.ai", name="Bob")

    head_a = {"Authorization": f"Bearer {tok_a}"}
    head_b = {"Authorization": f"Bearer {tok_b}"}

    # 1. Establish friendship: Alice sends request, Bob accepts
    req_res = client.post("/api/v1/friends/request", headers=head_a, json={"friend_id": user_b_id})
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    acc_res = client.post(f"/api/v1/friends/accept/{req_id}", headers=head_b)
    assert acc_res.status_code == 200

    # 2. Alice sends message to Bob
    send_res = client.post("/api/v1/friends/messages", headers=head_a, json={
        "friend_id": user_b_id,
        "message": "Hey Bob! Ready for our daily check-in?"
    })
    assert send_res.status_code == 201
    msg = send_res.json()
    assert msg["sender_id"] == user_a_id
    assert msg["recipient_id"] == user_b_id
    assert msg["content"] == "Hey Bob! Ready for our daily check-in?"

    # 3. Bob checks conversations list
    convs_res = client.get("/api/v1/friends/conversations", headers=head_b)
    assert convs_res.status_code == 200
    convs = convs_res.json()
    assert len(convs) >= 1
    assert convs[0]["unread_count"] == 1
    assert convs[0]["last_message"] == "Hey Bob! Ready for our daily check-in?"

    # 4. Bob reads message thread
    thread_res = client.get(f"/api/v1/friends/conversations/{user_a_id}/messages", headers=head_b)
    assert thread_res.status_code == 200
    thread = thread_res.json()
    assert len(thread) == 1
    assert thread[0]["content"] == "Hey Bob! Ready for our daily check-in?"

    # 5. Bob replies
    reply_res = client.post("/api/v1/friends/messages", headers=head_b, json={
        "friend_id": user_a_id,
        "message": "Yes! Just finished my coding session."
    })
    assert reply_res.status_code == 201

    # 6. Alice sees both messages in conversation
    alice_thread = client.get(f"/api/v1/friends/conversations/{user_b_id}/messages", headers=head_a)
    assert alice_thread.status_code == 200
    assert len(alice_thread.json()) == 2


def test_dashboard_real_data_and_zero_start(client):
    tok, u_id = get_auth_token(client, email="newbie_dashboard@planwise.ai", name="New User")
    head = {"Authorization": f"Bearer {tok}"}

    # Brand new user -> strict 0 baseline
    res = client.get("/api/v1/dashboard/", headers=head)
    assert res.status_code == 200
    d = res.json()
    assert d["today_tasks"] == 0
    assert d["completed_today"] == 0
    assert d["focus_minutes_today"] == 0
    assert d["productivity_score"] == 0
    assert d["current_streak"] == 0

    # Create 1 task and complete it
    t_res = client.post("/api/v1/tasks", headers=head, json={
        "title": "Initial Setup",
        "category": "Work",
        "is_completed": True,
        "due_date": datetime.utcnow().isoformat()
    })
    assert t_res.status_code == 201

    # Now dashboard reflects actual completion
    res2 = client.get("/api/v1/dashboard/", headers=head)
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["today_tasks"] >= 1
    assert d2["completed_today"] >= 1
    assert d2["productivity_score"] > 0


def test_ai_agent_tools(client):
    tok, u_id = get_auth_token(client, email="ai_agent_tester@planwise.ai", name="Agent Tester")
    head = {"Authorization": f"Bearer {tok}"}

    # 1. Ask agent to create task
    chat1 = client.post("/api/v1/ai/chat", headers=head, json={
        "message": "Create task: Write comprehensive unit tests !high"
    })
    assert chat1.status_code == 200
    assert "Created task" in chat1.json()["reply"]

    # 2. Ask agent to list tasks
    chat2 = client.post("/api/v1/ai/chat", headers=head, json={
        "message": "Show tasks"
    })
    assert chat2.status_code == 200
    assert "comprehensive unit tests" in chat2.json()["reply"].lower()
