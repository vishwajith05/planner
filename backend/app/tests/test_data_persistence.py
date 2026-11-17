"""
Test: Database persistence and data integrity across login sessions.

Verifies the core bug fix — data must NOT be erased when a user logs in,
and accounts must persist across sessions.
"""
import pytest
from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, password: str, name: str = "Test User"):
    """Helper: register a user and return the response."""
    return client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": name
    })


def _login(client: TestClient, email: str, password: str):
    """Helper: login and return (response, token)."""
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json().get("access_token") if res.status_code == 200 else None
    return res, token


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


class TestDataPersistenceAcrossLogins:
    """Verify that login does NOT erase existing data."""

    def test_user_data_persists_after_relogin(self, client: TestClient):
        """Register, create data, logout, login again — data must still be there."""
        # 1. Register user
        reg = _register(client, "persist@test.com", "StrongPass123!")
        assert reg.status_code == 201

        # 2. Login
        _, token = _login(client, "persist@test.com", "StrongPass123!")
        assert token is not None

        # 3. Create tasks
        for i in range(3):
            res = client.post("/api/v1/tasks", json={
                "title": f"Persistent Task {i+1}",
                "priority": "high",
                "category": "Work"
            }, headers=_auth_header(token))
            assert res.status_code == 201

        # 4. Verify tasks exist
        tasks = client.get("/api/v1/tasks", headers=_auth_header(token))
        assert len(tasks.json()) == 3

        # 5. "Logout" and login again (simulating the user's flow)
        _, token2 = _login(client, "persist@test.com", "StrongPass123!")
        assert token2 is not None

        # 6. Verify data is STILL there after re-login
        tasks_after = client.get("/api/v1/tasks", headers=_auth_header(token2))
        assert tasks_after.status_code == 200
        assert len(tasks_after.json()) == 3, (
            f"Expected 3 tasks after re-login, got {len(tasks_after.json())}. "
            "DATA WAS ERASED ON LOGIN!"
        )

    def test_account_persists_across_multiple_logins(self, client: TestClient):
        """Account must not be deleted after repeated logins."""
        _register(client, "multilogin@test.com", "Pass123!")
        
        # Login 5 times in a row
        for i in range(5):
            res, token = _login(client, "multilogin@test.com", "Pass123!")
            assert res.status_code == 200, f"Login #{i+1} failed: {res.json()}"
            
            # Verify profile is accessible
            me = client.get("/api/v1/auth/me", headers=_auth_header(token))
            assert me.status_code == 200
            assert me.json()["email"] == "multilogin@test.com"

    def test_multiple_users_data_isolation_persists(self, client: TestClient):
        """Two users' data must not interfere, and both persist across logins."""
        # Register two users
        _register(client, "alice@test.com", "AlicePass1!", "Alice")
        _register(client, "bob@test.com", "BobPass1!", "Bob")

        # Alice creates tasks
        _, alice_token = _login(client, "alice@test.com", "AlicePass1!")
        for i in range(2):
            client.post("/api/v1/tasks", json={"title": f"Alice Task {i+1}"}, 
                        headers=_auth_header(alice_token))

        # Bob creates tasks
        _, bob_token = _login(client, "bob@test.com", "BobPass1!")
        client.post("/api/v1/tasks", json={"title": "Bob Task 1"}, 
                    headers=_auth_header(bob_token))

        # Both re-login
        _, alice_token2 = _login(client, "alice@test.com", "AlicePass1!")
        _, bob_token2 = _login(client, "bob@test.com", "BobPass1!")

        # Verify isolation persists
        alice_tasks = client.get("/api/v1/tasks", headers=_auth_header(alice_token2))
        bob_tasks = client.get("/api/v1/tasks", headers=_auth_header(bob_token2))

        assert len(alice_tasks.json()) == 2, "Alice's tasks were lost!"
        assert len(bob_tasks.json()) == 1, "Bob's tasks were lost!"

    def test_goals_habits_persist_after_login(self, client: TestClient):
        """Goals and habits must also survive re-login."""
        _register(client, "goals@test.com", "GoalPass1!")
        _, token = _login(client, "goals@test.com", "GoalPass1!")
        h = _auth_header(token)

        # Create a goal
        goal_res = client.post("/api/v1/goals/", json={
            "title": "Learn Python",
            "category": "Education",
            "priority": "high"
        }, headers=h)
        assert goal_res.status_code == 201

        # Create a habit
        habit_res = client.post("/api/v1/habits/", json={
            "title": "Read 30 minutes",
            "category": "Education",
            "frequency": "daily"
        }, headers=h)
        assert habit_res.status_code == 201

        # Re-login
        _, token2 = _login(client, "goals@test.com", "GoalPass1!")
        h2 = _auth_header(token2)

        # Verify persistence
        goals = client.get("/api/v1/goals/", headers=h2)
        habits = client.get("/api/v1/habits/", headers=h2)
        assert len(goals.json()) == 1, "Goal was lost after re-login!"
        assert len(habits.json()) == 1, "Habit was lost after re-login!"

    def test_db_health_check_endpoint(self, client: TestClient):
        """The new /health/db endpoint should report database status."""
        res = client.get("/api/v1/health/db")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "user_count" in data

    def test_db_health_shows_users_after_registration(self, client: TestClient):
        """After registering a user, /health/db should show user_count > 0."""
        _register(client, "healthcheck@test.com", "HealthPass1!")
        
        res = client.get("/api/v1/health/db")
        data = res.json()
        assert data["user_count"] >= 1, "DB health check shows 0 users after registration!"
        assert data["warning"] is None, "DB health check incorrectly shows empty warning!"
