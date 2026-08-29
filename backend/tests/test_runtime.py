def _create_machine(client, auth_headers, code="RUNTIME-TEST"):
    return client.post("/api/machines", json={
        "machine_code": code, "name": "Runtime Motor", "location": "Bay Y",
    }, headers=auth_headers).json()


def test_start_and_get_runtime_status(client, auth_headers):
    machine = _create_machine(client, auth_headers)

    resp = client.post(f"/api/machines/{machine['id']}/runtime/start",
                        json={"duration_seconds": 600}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "RUNNING"
    assert data["configured_seconds"] == 600

    resp = client.get(f"/api/machines/{machine['id']}/runtime", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "RUNNING"


def test_stop_runtime(client, auth_headers):
    machine = _create_machine(client, auth_headers)
    client.post(f"/api/machines/{machine['id']}/runtime/start",
                json={"duration_seconds": 600}, headers=auth_headers)

    resp = client.post(f"/api/machines/{machine['id']}/runtime/stop", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "STOPPED"


def test_start_runtime_rejects_nonpositive_duration(client, auth_headers):
    machine = _create_machine(client, auth_headers)
    resp = client.post(f"/api/machines/{machine['id']}/runtime/start",
                        json={"duration_seconds": 0}, headers=auth_headers)
    assert resp.status_code == 400


def test_runtime_status_for_never_started_machine(client, auth_headers):
    machine = _create_machine(client, auth_headers)
    resp = client.get(f"/api/machines/{machine['id']}/runtime", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "STOPPED"
