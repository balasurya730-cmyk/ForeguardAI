"""
Shared handling for incoming sensor/gas payloads, whichever transport they
arrived through (real MQTT topic or the demo simulator calling directly).
"""
import logging

from app.database import SessionLocal
from app.models.machine import Machine
from app.models.gas_zone import GasZone
from app.services import machine_service
from app.services.gas_service import ingest_gas_reading

logger = logging.getLogger("forgeguard.mqtt_handlers")


async def handle_incoming_message(topic: str, payload: dict):
    parts = topic.split("/")
    if len(parts) != 3:
        return
    _base, entity, kind = parts

    db = SessionLocal()
    try:
        if kind == "sensors":
            machine = db.query(Machine).filter(Machine.machine_code == entity).first()
            if not machine:
                logger.warning("Unknown machine_code in MQTT payload: %s", entity)
                return
            await machine_service.ingest_sensor_reading(
                db,
                machine,
                temperature=payload.get("temperature", machine.temperature),
                voltage=payload.get("voltage", machine.voltage),
                current=payload.get("current", machine.current),
                vibration=payload.get("vibration", machine.vibration),
            )
        elif kind == "gas":
            zone = db.query(GasZone).filter(GasZone.zone_name == entity).first()
            if not zone:
                logger.warning("Unknown zone_name in MQTT payload: %s", entity)
                return
            await ingest_gas_reading(db, zone, payload.get("ppm", zone.current_ppm))
    finally:
        db.close()
