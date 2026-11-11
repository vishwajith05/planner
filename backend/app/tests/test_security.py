def test_owasp_security_headers_present(client):
    res = client.get("/")
    assert res.status_code == 200
    headers = res.headers

    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"


def test_auth_rate_limiting_protection(client):
    headers = {"x-test-rate-limit": "true", "x-client-id": "test-attacker-ip"}
    # Make multiple failed login requests in rapid succession
    for _ in range(5):
        client.post("/api/v1/auth/login", headers=headers, json={
            "email": "attacker@unknown.com",
            "password": "WrongPassword!"
        })

    # The 6th request should be throttled with HTTP 429
    res = client.post("/api/v1/auth/login", headers=headers, json={
        "email": "attacker@unknown.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 429
    assert "Too many requests" in res.json()["detail"]
