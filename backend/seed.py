"""
Seed the database with demonstration data:
  - 3 users (admin/manager/operator)
  - 8 machines
  - 24 workers
  - 4 cameras
  - 3 gas zones
  - ~48h of historical sensor readings per machine
  - a handful of safety events / alerts

Run with:  python seed.py
Safe to re-run: it clears and recreates all tables first.
"""
import random
from datetime import datetime, timedelta

from app.database import Base, engine, SessionLocal
import app.models  # noqa: F401
from app.models.user import User, UserRole
from app.models.machine import Machine, MachineStatus
from app.models.sensor_reading import SensorReading
from app.models.worker import Worker
from app.models.camera import Camera
from app.models.gas_zone import GasZone, GasZoneStatus
from app.models.safety_event import SafetyEvent, ViolationType
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.auth import hash_password

random.seed(42)

print("Dropping and recreating all tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ---------------------------------------------------------------- users ----
print("Seeding users...")
users = [
    User(full_name="Ava Admin", email="admin@forgeguard.ai", hashed_password=hash_password("Admin@123"), role=UserRole.ADMIN, is_active=1),
    User(full_name="Mark Manager", email="manager@forgeguard.ai", hashed_password=hash_password("Manager@123"), role=UserRole.MANAGER, is_active=1),
    User(full_name="Olive Operator", email="operator@forgeguard.ai", hashed_password=hash_password("Operator@123"), role=UserRole.OPERATOR, is_active=1),
]
db.add_all(users)
db.commit()

# ------------------------------------------------------------- machines ----
print("Seeding machines...")
machine_defs = [
    ("MOTOR-01", "Induction Motor 01", "Bay A"),
    ("MOTOR-02", "Induction Motor 02", "Bay A"),
    ("CNC-01", "CNC Lathe 01", "Bay B"),
    ("CNC-02", "CNC Lathe 02", "Bay B"),
    ("PRESS-01", "Hydraulic Press 01", "Bay C"),
    ("PRESS-02", "Hydraulic Press 02", "Bay C"),
    ("CONV-01", "Conveyor Line 01", "Bay D"),
    ("COMP-01", "Air Compressor 01", "Utility Room"),
]
machines = []
for code, name, location in machine_defs:
    m = Machine(
        machine_code=code,
        name=name,
        location=location,
        status=MachineStatus.NORMAL,
        temperature=round(random.uniform(40, 55), 1),
        voltage=round(random.uniform(225, 235), 1),
        current=round(random.uniform(2.5, 5.0), 2),
        vibration=round(random.uniform(1.0, 2.5), 2),
        health_score=round(random.uniform(88, 98), 1),
        is_running=random.choice([0, 1]),
    )
    machines.append(m)
db.add_all(machines)
db.commit()

print("Seeding 48h of historical sensor readings...")
now = datetime.utcnow()
for m in machines:
    base_temp = m.temperature
    base_voltage = m.voltage
    base_current = m.current
    base_vibration = m.vibration
    for hours_ago in range(48, 0, -2):
        ts = now - timedelta(hours=hours_ago)
        reading = SensorReading(
            machine_id=m.id,
            temperature=round(base_temp + random.uniform(-4, 4), 1),
            voltage=round(base_voltage + random.uniform(-3, 3), 1),
            current=round(max(0.1, base_current + random.uniform(-0.8, 0.8)), 2),
            vibration=round(max(0.1, base_vibration + random.uniform(-0.5, 0.5)), 2),
            recorded_at=ts,
        )
        db.add(reading)
db.commit()

# -------------------------------------------------------------- workers ----
print("Seeding 24 workers...")
departments = ["Assembly", "Machining", "Press Shop", "Logistics", "Maintenance"]
shifts = ["Morning", "Afternoon", "Night"]
first_names = ["Raj", "Priya", "Arjun", "Divya", "Karthik", "Meena", "Vikram", "Anita",
               "Suresh", "Lakshmi", "Ravi", "Kavya", "Sanjay", "Deepa", "Manoj", "Pooja",
               "Ajay", "Sneha", "Vijay", "Nisha", "Rahul", "Swathi", "Kiran", "Anjali"]
workers = []
for i, fname in enumerate(first_names, start=1):
    w = Worker(
        worker_code=f"WORKER-{i:02d}",
        full_name=f"{fname} Kumar",
        department=random.choice(departments),
        shift=random.choice(shifts),
    )
    workers.append(w)
db.add_all(workers)
db.commit()

# -------------------------------------------------------------- cameras ----
print("Seeding cameras...")
cameras = [
    Camera(camera_code="C01", name="Bay A Entrance", location="Bay A"),
    Camera(camera_code="C02", name="Bay B Floor", location="Bay B"),
    Camera(camera_code="C03", name="Press Shop", location="Bay C"),
    Camera(camera_code="C04", name="Loading Dock", location="Logistics"),
]
db.add_all(cameras)
db.commit()

# ------------------------------------------------------------ gas zones ----
print("Seeding gas zones...")
gas_zones = [
    GasZone(zone_name="ZONE A", gas_type="LPG", current_ppm=120, warning_threshold=300, critical_threshold=600, status=GasZoneStatus.SAFE),
    GasZone(zone_name="ZONE B", gas_type="CO", current_ppm=420, warning_threshold=350, critical_threshold=700, status=GasZoneStatus.WARNING),
    GasZone(zone_name="ZONE C", gas_type="LPG", current_ppm=105, warning_threshold=300, critical_threshold=600, status=GasZoneStatus.SAFE),
]
db.add_all(gas_zones)
db.commit()

# --------------------------------------------------------- safety events ----
print("Seeding safety events + alerts...")
violation_types = list(ViolationType)
safety_events = []
for _ in range(15):
    worker = random.choice(workers)
    camera = random.choice(cameras)
    vtype = random.choice(violation_types)
    ts = now - timedelta(hours=random.randint(0, 72))
    ev = SafetyEvent(
        worker_id=worker.id,
        camera_id=camera.id,
        violation_type=vtype,
        confidence=round(random.uniform(0.8, 0.99), 2),
        duration_seconds=round(random.uniform(3, 25), 1),
        evidence_path=f"/uploads/images/seed_{vtype.value.lower()}_{worker.id}.jpg",
        reviewed=random.choice([True, False]),
        timestamp=ts,
    )
    safety_events.append(ev)
db.add_all(safety_events)
db.commit()

alerts = []
for m in random.sample(machines, 3):
    alerts.append(Alert(
        alert_type=AlertType.HIGH_TEMPERATURE,
        severity=AlertSeverity.WARNING,
        message=f"{m.name} temperature elevated",
        related_machine_id=m.id,
        status=random.choice(list(AlertStatus)),
        created_at=now - timedelta(hours=random.randint(0, 48)),
    ))
for ev in safety_events[:6]:
    alert_type = {
        ViolationType.NO_HELMET: AlertType.NO_HELMET,
        ViolationType.NO_PPE: AlertType.NO_PPE,
        ViolationType.MOBILE_USAGE: AlertType.MOBILE_USAGE,
    }[ev.violation_type]
    alerts.append(Alert(
        alert_type=alert_type,
        severity=AlertSeverity.WARNING,
        message=f"{ev.violation_type.value.replace('_',' ').title()} detected for worker #{ev.worker_id}",
        related_worker_id=ev.worker_id,
        status=random.choice(list(AlertStatus)),
        created_at=ev.timestamp,
    ))
alerts.append(Alert(
    alert_type=AlertType.GAS_WARNING,
    severity=AlertSeverity.WARNING,
    message="ZONE B gas level elevated at 420 ppm (CO)",
    related_zone_id=gas_zones[1].id,
    status=AlertStatus.ACTIVE,
    created_at=now - timedelta(hours=1),
))
db.add_all(alerts)
db.commit()

db.close()

print("\nSeed complete!")
print("Login with:")
print("  admin@forgeguard.ai / Admin@123")
print("  manager@forgeguard.ai / Manager@123")
print("  operator@forgeguard.ai / Operator@123")
