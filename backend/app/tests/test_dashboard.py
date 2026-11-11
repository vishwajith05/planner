def test_dashboard_summary_endpoint(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "greeting" in data
    assert "productivity_score" in data
    assert data["productivity_score"] >= 0
    assert "today_tasks" in data
    assert isinstance(data["today_tasks"], list)
    assert len(data["today_tasks"]) > 0
    assert "ai_tip" in data
