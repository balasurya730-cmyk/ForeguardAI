"""
DEMO MODE simulator.

When SYSTEM_MODE=DEMO (the default, no hardware required), this background
task periodically generates realistic, slowly-drifting sensor readings,
gas levels, and occasional worker-safety violations, and pushes them
through the exact same ingestion services real ESP32/MQTT/YOLO data would
use (machine_service.ingest_sensor_reading, gas_service.ingest_gas_reading,
safety_service.record_violation). This means the dashboard, alert engine
and WebSocket broadcasts behave identically in demo and live mode -- only
the data source differs.
"""
import asyncio
import logging
import random

from app.database import SessionLocal
from app.models.machine import Machine
from app.models.gas_zone import GasZone
from app.models.worker import Worker
from app.models.camera import Camera
from app.models.safety_event import ViolationType
from app.services import machine_service
from app.services.gas_service import ingest_gas_reading
from app.services import safety_service

logger = logging.getLogger("forgeguard.demo_simulator")

# Per-machine drift state so values wander smoothly instead of jumping randomly.
_machine_state: dict[int, dict] = {}
_zone_state: dict[int, dict] = {}


def _drift(value, target, max_step, jitter):
    value += (target - value) * 0.05 + random.uniform(-jitter, jitter)
    value += random.uniform(-max_step, max_step)
    return value


async def _simulate_machines(db):
    machines = db.query(Machine).all()
    for machine in machines:
        state = _machine_state.setdefault(
            machine.id,
            {
                "temperature": machine.temperature or 45.0,
                "voltage": machine.voltage or machine.voltage_nominal,
                "current": machine.current or 3.0,
                "vibration": machine.vibration or 1.5,
                "spike_ttl": 0,
            },
        )

        # Occasionally inject a short "spike" so WARNING/CRITICAL states and
        # alerts are demonstrable, then relax back to normal.
        if state["spike_ttl"] <= 0 and random.random() < 0.03:
            state["spike_ttl"] = random.randint(3, 8)
        if state["spike_ttl"] > 0:
            state["temperature"] = _drift(state["temperature"], machine.temp_critical + 5, 2.0, 1.0)
            state["current"] = _drift(state["current"], machine.current_critical + 1, 0.6, 0.3)
            state["vibration"] = _drift(state["vibration"], machine.vibration_critical + 1, 0.5, 0.3)
            state["spike_ttl"] -= 1
        else:
            state["temperature"] = _drift(state["temperature"], 45.0, 0.8, 0.4)
            state["current"] = _drift(state["current"], 3.5, 0.3, 0.15)
            state["vibration"] = _drift(state["vibration"], 1.5, 0.2, 0.1)

        state["voltage"] = _drift(state["voltage"], machine.voltage_nominal, 1.5, 1.0)

        await machine_service.ingest_sensor_reading(
            db,
            machine,
            temperature=round(max(20.0, state["temperature"]), 1),
            voltage=round(state["voltage"], 1),
            current=round(max(0.0, state["current"]), 2),
            vibration=round(max(0.0, state["vibration"]), 2),
        )


async def _simulate_gas(db):
    zones = db.query(GasZone).all()
    for zone in zones:
        state = _zone_state.setdefault(zone.id, {"ppm": zone.current_ppm or 100.0, "spike_ttl": 0})

        if state["spike_ttl"] <= 0 and random.random() < 0.02:
            state["spike_ttl"] = random.randint(3, 6)
        if state["spike_ttl"] > 0:
            state["ppm"] = _drift(state["ppm"], zone.critical_threshold + 50, 20, 10)
            state["spike_ttl"] -= 1
        else:
            state["ppm"] = _drift(state["ppm"], zone.warning_threshold * 0.4, 10, 5)

        await ingest_gas_reading(db, zone, round(max(0.0, state["ppm"]), 0))


async def _simulate_safety(db):
    """Occasionally emit a helmet/PPE/mobile violation, mirroring what the
    YOLO + ByteTrack + rule-engine pipeline would produce in LIVE mode once
    a detection has persisted for the configured duration."""
    workers = db.query(Worker).all()
    cameras = db.query(Camera).all()
    if not workers or not cameras:
        return

    if random.random() < 0.06:
        worker = random.choice(workers)
        camera = random.choice(cameras)
        violation_type = random.choice(list(ViolationType))
        confidence = round(random.uniform(0.80, 0.98), 2)
        duration = round(random.uniform(3.0, 20.0), 1)

        await safety_service.record_violation(
            db,
            worker_id=worker.id,
            camera_id=camera.id,
            violation_type=violation_type,
            confidence=confidence,
            duration_seconds=duration,
            evidence_image_path=f"/uploads/images/demo_{violation_type.value.lower()}_{worker.id}.jpg",
        )


async def demo_simulator_loop(interval_seconds: float = 4.0):
    logger.info("Demo simulator started (interval=%ss)", interval_seconds)
    while True:
        db = SessionLocal()
        try:
            await _simulate_machines(db)
            await _simulate_gas(db)
            await _simulate_safety(db)
        except Exception:
            logger.exception("Demo simulator tick failed")
        finally:
            db.close()
        await asyncio.sleep(interval_seconds)
