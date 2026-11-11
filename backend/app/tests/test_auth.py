def test_register_and_login_flow(client):
    # 1. Register new user
    register_payload = {
        "email": "architect@planwise.ai",
        "password": "SecurePassword123!",
        "full_name": "Chief Architect",
        "timezone": "America/New_York"
    }
    reg_res = client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == "architect@planwise.ai"
    assert user_data["full_name"] == "Chief Architect"
    assert "id" in user_data

    # 2. Duplicate registration should fail
    dup_res = client.post("/api/v1/auth/register", json=register_payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # 3. Login with wrong password should fail
    wrong_login = client.post("/api/v1/auth/login", json={
        "email": "architect@planwise.ai",
        "password": "WrongPassword!"
    })
    assert wrong_login.status_code == 401

    # 4. Login with correct password
    login_res = client.post("/api/v1/auth/login", json={
        "email": "architect@planwise.ai",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    auth_data = login_res.json()
    assert "access_token" in auth_data
    token = auth_data["access_token"]

    # 5. Get current profile using bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "architect@planwise.ai"

    # 6. Update profile
    update_res = client.put(
        "/api/v1/auth/me",
        headers=headers,
        json={"full_name": "Senior Lead Architect", "bio": "Productivity Enthusiast"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["full_name"] == "Senior Lead Architect"
    assert update_res.json()["bio"] == "Productivity Enthusiast"

def test_unauthorized_access_fails(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
