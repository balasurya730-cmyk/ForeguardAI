def test_create_gas_zone(client, auth_headers):
    resp = client.post("/api/gas/zones", json={
        "zone_name": "ZONE-TEST",
        "gas_type": "LPG",
        "warning_threshold": 300,
        "critical_threshold": 600,
    }, headers=auth_headers)
    assert resp.status_code == 201
    zone = resp.json()
    assert zone["status"] == "SAFE"


def test_gas_ingestion_via_sensor_endpoint_triggers_warning(client, auth_headers):
    client.post("/api/machines", json={"machine_code": "M-GAS", "name": "M", "location": "L"}, headers=auth_headers)
    client.post("/api/gas/zones", json={
        "zone_name": "ZONE-TEST2", "gas_type": "LPG", "warning_threshold": 300, "critical_threshold": 600,
    }, headers=auth_headers)

    resp = client.post("/api/sensors/data", json={
        "machine_code": "M-GAS", "temperature": 40, "voltage": 230, "current": 2, "vibration": 1,
        "gas_ppm": 350, "zone_name": "ZONE-TEST2",
    })
    assert resp.status_code == 202

    resp = client.get("/api/gas/zones", headers=auth_headers)
    zone = next(z for z in resp.json() if z["zone_name"] == "ZONE-TEST2")
    assert zone["status"] == "WARNING"
    assert zone["current_ppm"] == 350


def test_gas_ingestion_critical_threshold(client, auth_headers):
    client.post("/api/machines", json={"machine_code": "M-GAS2", "name": "M", "location": "L"}, headers=auth_headers)
    client.post("/api/gas/zones", json={
        "zone_name": "ZONE-TEST3", "gas_type": "CO", "warning_threshold": 300, "critical_threshold": 600,
    }, headers=auth_headers)

    client.post("/api/sensors/data", json={
        "machine_code": "M-GAS2", "temperature": 40, "voltage": 230, "current": 2, "vibration": 1,
        "gas_ppm": 700, "zone_name": "ZONE-TEST3",
    })

    resp = client.get("/api/gas/zones", headers=auth_headers)
    zone = next(z for z in resp.json() if z["zone_name"] == "ZONE-TEST3")
    assert zone["status"] == "CRITICAL"

    # A CRITICAL alert should have been raised
    resp = client.get("/api/alerts", headers=auth_headers)
    alert_types = [a["alert_type"] for a in resp.json()]
    assert "GAS_CRITICAL" in alert_types


def test_update_zone_thresholds(client, auth_headers):
    zone = client.post("/api/gas/zones", json={
        "zone_name": "ZONE-TEST4", "gas_type": "LPG", "warning_threshold": 300, "critical_threshold": 600,
    }, headers=auth_headers).json()

    resp = client.put(f"/api/gas/zones/{zone['id']}", json={"warning_threshold": 250}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["warning_threshold"] == 250
