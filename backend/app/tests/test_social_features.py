import pytest
from fastapi.testclient import TestClient

def test_friend_growth_workflow(client: TestClient):
    # 1. Register User A and User B
    u_a = client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "password": "Password123!",
        "full_name": "Alice Wonderland"
    }).json()

    u_b = client.post("/api/v1/auth/register", json={
        "email": "bob@example.com",
        "password": "Password123!",
        "full_name": "Bob Builder"
    }).json()

    # Login both
    token_a = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "Password123!"}).json()["access_token"]
    token_b = client.post("/api/v1/auth/login", json={"email": "bob@example.com", "password": "Password123!"}).json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. Search users from Alice's account
    search_res = client.get("/api/v1/friends/search?q=bob", headers=headers_a)
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1
    assert search_res.json()[0]["email"] == "bob@example.com"

    # 3. Send friend request from Alice to Bob
    req_res = client.post("/api/v1/friends/request", json={"addressee_email": "bob@example.com"}, headers=headers_a)
    assert req_res.status_code == 201
    friendship_id = req_res.json()["id"]

    # 4. Check Bob's pending requests
    pending_res = client.get("/api/v1/friends/requests/pending", headers=headers_b)
    assert pending_res.status_code == 200
    assert len(pending_res.json()) == 1
    assert pending_res.json()[0]["requester_email"] == "alice@example.com"

    # 5. Bob accepts the request
    accept_res = client.put(f"/api/v1/friends/request/{friendship_id}/accept", headers=headers_b)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "accepted"

    # 6. Check friends list for both
    friends_a = client.get("/api/v1/friends/", headers=headers_a).json()
    friends_b = client.get("/api/v1/friends/", headers=headers_b).json()
    assert len(friends_a) == 1
    assert friends_a[0]["email"] == "bob@example.com"
    assert len(friends_b) == 1
    assert friends_b[0]["email"] == "alice@example.com"

    # 7. Create a shared challenge
    ch_res = client.post("/api/v1/friends/challenges", json={
        "title": "30-Day Cybersecurity Sprint",
        "description": "Daily labs and study",
        "duration_days": 30,
        "daily_target": "Complete 1 room",
        "friend_ids": [friends_a[0]["id"]]
    }, headers=headers_a)
    assert ch_res.status_code == 201
    challenge_id = ch_res.json()["id"]

    # 8. Update challenge progress
    prog_res = client.put(f"/api/v1/friends/challenges/{challenge_id}/progress", json={
        "progress_percent": 25,
        "days_completed": 7
    }, headers=headers_a)
    assert prog_res.status_code == 200

    # 9. Send encouragement message
    enc_res = client.post("/api/v1/friends/encourage", json={
        "recipient_id": friends_a[0]["id"],
        "message": "Keep up the great work!",
        "challenge_id": challenge_id
    }, headers=headers_a)
    assert enc_res.status_code == 201
    msg_id = enc_res.json()["id"]

    # Bob views messages
    msgs_res = client.get("/api/v1/friends/messages", headers=headers_b)
    assert msgs_res.status_code == 200
    assert len(msgs_res.json()) == 1
    assert msgs_res.json()[0]["message"] == "Keep up the great work!"

    # Bob marks message as read
    client.put(f"/api/v1/friends/messages/{msg_id}/read", headers=headers_b)

    # 10. Focus together session
    focus_res = client.post("/api/v1/friends/focus", json={
        "title": "Co-working Session",
        "duration_minutes": 25
    }, headers=headers_a)
    assert focus_res.status_code == 201
    code = focus_res.json()["session_code"]

    # Bob joins
    join_res = client.post(f"/api/v1/friends/focus/join/{code}", headers=headers_b)
    assert join_res.status_code == 200


def test_growth_couple_workflow(client: TestClient):
    # 1. Register Partner A and Partner B
    client.post("/api/v1/auth/register", json={
        "email": "charlie@example.com",
        "password": "Password123!",
        "full_name": "Charlie Brown"
    })
    client.post("/api/v1/auth/register", json={
        "email": "diana@example.com",
        "password": "Password123!",
        "full_name": "Diana Prince"
    })

    token_c = client.post("/api/v1/auth/login", json={"email": "charlie@example.com", "password": "Password123!"}).json()["access_token"]
    token_d = client.post("/api/v1/auth/login", json={"email": "diana@example.com", "password": "Password123!"}).json()["access_token"]

    headers_c = {"Authorization": f"Bearer {token_c}"}
    headers_d = {"Authorization": f"Bearer {token_d}"}

    # 2. Charlie generates couple invite
    inv_res = client.post("/api/v1/couple/invite", headers=headers_c)
    assert inv_res.status_code == 201
    invite_code = inv_res.json()["invite_code"]

    # 3. Diana accepts invite
    accept_res = client.post("/api/v1/couple/accept", json={"invite_code": invite_code}, headers=headers_d)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "active"

    # 4. Get couple status
    couple_info = client.get("/api/v1/couple/", headers=headers_c).json()
    assert couple_info["status"] == "active"
    assert couple_info["partner_b"]["email"] == "diana@example.com"

    # 5. Create shared goal
    goal_res = client.post("/api/v1/couple/goals", json={
        "title": "Learn Cloud Architecture",
        "description": "AWS Solutions Architect exam",
        "category": "Education"
    }, headers=headers_c)
    assert goal_res.status_code == 201
    goal_id = goal_res.json()["id"]

    # Charlie updates his progress to 60%
    client.put(f"/api/v1/couple/goals/{goal_id}/progress", json={"progress": 60}, headers=headers_c)

    # Diana updates her progress to 40%
    goal_updated = client.put(f"/api/v1/couple/goals/{goal_id}/progress", json={"progress": 40}, headers=headers_d).json()
    assert goal_updated["partner_a_progress"] == 60
    assert goal_updated["partner_b_progress"] == 40
    assert goal_updated["combined_progress"] == 50.0

    # 6. Create shared habit & toggle
    habit_res = client.post("/api/v1/couple/habits", json={
        "title": "Morning Walk & Talk",
        "frequency": "daily"
    }, headers=headers_c)
    assert habit_res.status_code == 201
    habit_id = habit_res.json()["id"]

    # Charlie toggles habit
    toggle_c = client.put(f"/api/v1/couple/habits/{habit_id}/toggle", headers=headers_c).json()
    assert toggle_c["done"] is True
    assert toggle_c["my_streak"] == 1

    # 7. Submit check-in
    checkin_res = client.post("/api/v1/couple/checkins", json={
        "mood": "great",
        "gratitude": "Supportive partner",
        "win_of_day": "Passed mock exam",
        "support_needed": "Coffee break together"
    }, headers=headers_c)
    assert checkin_res.status_code == 201

    checkins = client.get("/api/v1/couple/checkins", headers=headers_d).json()
    assert len(checkins) == 1
    assert checkins[0]["mood"] == "great"

    # 8. AI Suggestions
    ai_sugg = client.get("/api/v1/couple/ai-suggestions", headers=headers_c).json()
    assert len(ai_sugg["suggestions"]) >= 3
