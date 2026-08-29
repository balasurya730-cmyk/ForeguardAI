def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={
        "full_name": "Jane Doe",
        "email": "jane@forgeguard.ai",
        "password": "Secret@123",
        "role": "MANAGER",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == "jane@forgeguard.ai"
    assert "access_token" in data

    resp = client.post("/api/auth/login", json={"email": "jane@forgeguard.ai", "password": "Secret@123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "full_name": "Jane Doe", "email": "jane2@forgeguard.ai", "password": "Secret@123",
    })
    resp = client.post("/api/auth/login", json={"email": "jane2@forgeguard.ai", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    payload = {"full_name": "Dup User", "email": "dup@forgeguard.ai", "password": "Secret@123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 400


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "ADMIN"
