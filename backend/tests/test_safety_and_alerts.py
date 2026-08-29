def test_create_safety_event_creates_evidence_and_alert(client, auth_headers):
    resp = client.post("/api/safety/events", json={
        "violation_type": "NO_HELMET",
        "confidence": 0.94,
        "duration_seconds": 12.0,
        "evidence_path": "/uploads/images/test.jpg",
    })
    assert resp.status_code == 201
    event = resp.json()
    assert event["violation_type"] == "NO_HELMET"

    resp = client.get("/api/evidence", headers=auth_headers)
    assert len(resp.json()) == 1
    assert resp.json()[0]["event_type"] == "NO_HELMET"

    resp = client.get("/api/alerts", headers=auth_headers)
    alert_types = [a["alert_type"] for a in resp.json()]
    assert "NO_HELMET" in alert_types


def test_mobile_usage_violation(client, auth_headers):
    resp = client.post("/api/safety/events", json={
        "violation_type": "MOBILE_USAGE",
        "confidence": 0.91,
        "duration_seconds": 17.0,
    })
    assert resp.status_code == 201
    assert resp.json()["violation_type"] == "MOBILE_USAGE"


def test_list_safety_events(client, auth_headers):
    client.post("/api/safety/events", json={"violation_type": "NO_PPE", "confidence": 0.8, "duration_seconds": 5})
    resp = client.get("/api/safety/events", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_mark_evidence_reviewed(client, auth_headers):
    client.post("/api/safety/events", json={"violation_type": "NO_HELMET", "confidence": 0.9, "duration_seconds": 8})
    evidence = client.get("/api/evidence", headers=auth_headers).json()[0]

    resp = client.put(f"/api/evidence/{evidence['id']}/reviewed", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["reviewed"] is True


def test_acknowledge_and_resolve_alert(client, auth_headers):
    client.post("/api/safety/events", json={"violation_type": "NO_HELMET", "confidence": 0.9, "duration_seconds": 8})
    alert = client.get("/api/alerts", headers=auth_headers).json()[0]

    resp = client.put(f"/api/alerts/{alert['id']}/acknowledge", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACKNOWLEDGED"

    resp = client.put(f"/api/alerts/{alert['id']}/resolve", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "RESOLVED"


def test_filter_alerts_by_status(client, auth_headers):
    client.post("/api/safety/events", json={"violation_type": "NO_HELMET", "confidence": 0.9, "duration_seconds": 8})
    resp = client.get("/api/alerts", params={"status": "ACTIVE"}, headers=auth_headers)
    assert resp.status_code == 200
    assert all(a["status"] == "ACTIVE" for a in resp.json())
