def _create_machine(client, auth_headers, code="MOTOR-TEST"):
    resp = client.post("/api/machines", json={
        "machine_code": code,
        "name": "Test Motor",
        "location": "Bay X",
    }, headers=auth_headers)
    return resp


def test_create_and_list_machines(client, auth_headers):
    resp = _create_machine(client, auth_headers)
    assert resp.status_code == 201
    machine = resp.json()
    assert machine["machine_code"] == "MOTOR-TEST"
    assert machine["status"] == "NORMAL"

    resp = client.get("/api/machines", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_duplicate_machine_code_rejected(client, auth_headers):
    _create_machine(client, auth_headers)
    resp = _create_machine(client, auth_headers)
    assert resp.status_code == 400


def test_get_machine_not_found(client, auth_headers):
    resp = client.get("/api/machines/999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_machine(client, auth_headers):
    machine = _create_machine(client, auth_headers).json()
    resp = client.put(f"/api/machines/{machine['id']}", json={"location": "Bay Z"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["location"] == "Bay Z"


def test_delete_machine_requires_admin(client, auth_headers):
    machine = _create_machine(client, auth_headers).json()
    resp = client.delete(f"/api/machines/{machine['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_sensor_ingestion_updates_machine_and_creates_reading(client, auth_headers):
    machine = _create_machine(client, auth_headers).json()

    resp = client.post("/api/sensors/data", json={
        "machine_code": "MOTOR-TEST",
        "temperature": 50.0,
        "voltage": 230.0,
        "current": 3.0,
        "vibration": 1.0,
    })
    assert resp.status_code == 202

    resp = client.get(f"/api/machines/{machine['id']}", headers=auth_headers)
    updated = resp.json()
    assert updated["temperature"] == 50.0
    assert updated["status"] == "NORMAL"

    resp = client.get(f"/api/machines/{machine['id']}/readings", headers=auth_headers)
    assert len(resp.json()) == 1


def test_sensor_ingestion_triggers_warning_status(client, auth_headers):
    _create_machine(client, auth_headers)

    resp = client.post("/api/sensors/data", json={
        "machine_code": "MOTOR-TEST",
        "temperature": 90.0,  # above default temp_critical=80
        "voltage": 230.0,
        "current": 3.0,
        "vibration": 1.0,
    })
    assert resp.status_code == 202

    resp = client.get("/api/machines", headers=auth_headers)
    machine = resp.json()[0]
    assert machine["status"] == "CRITICAL"


def test_sensor_ingestion_unknown_machine_code(client, auth_headers):
    resp = client.post("/api/sensors/data", json={
        "machine_code": "DOES-NOT-EXIST",
        "temperature": 50.0, "voltage": 230.0, "current": 3.0, "vibration": 1.0,
    })
    assert resp.status_code == 404
