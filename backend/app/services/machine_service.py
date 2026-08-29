"""
Machine health scoring and sensor-data ingestion.

This is the single entry point sensor data flows through, whether it
originates from a real ESP32 (via MQTT), a manual POST to
/api/sensors/data, or the built-in demo simulator. It:

  1. Updates the machine's live sensor values
  2. Recomputes a 0-100 health score
  3. Derives NORMAL / WARNING / CRITICAL status
  4. Persists a historical SensorReading row
  5. Raises alerts through the alert engine when thresholds are crossed
  6. Broadcasts the update over WebSocket so the dashboard refreshes live
"""
from sqlalchemy.orm import Session

from app.models.machine import Machine, MachineStatus
from app.models.sensor_reading import SensorReading
from app.models.alert import AlertType, AlertSeverity
from app.services import alert_service
from app.websocket.manager import manager


def compute_health_score(machine: Machine, temperature: float, voltage: float, current: float, vibration: float) -> float:
    """Weighted deviation-from-nominal scoring, clamped to [0, 100].

    Each sensor contributes a penalty proportional to how far past its
    warning/critical thresholds the reading is. This keeps the score
    interpretable (100 = perfectly nominal) while still reacting sharply
    once a machine crosses into WARNING/CRITICAL territory.
    """
    score = 100.0

    if temperature > machine.temp_warning:
        span = max(machine.temp_critical - machine.temp_warning, 1e-6)
        over = min((temperature - machine.temp_warning) / span, 1.5)
        score -= over * 35

    voltage_dev = abs(voltage - machine.voltage_nominal)
    if voltage_dev > machine.voltage_tolerance:
        over = min((voltage_dev - machine.voltage_tolerance) / max(machine.voltage_tolerance, 1e-6), 1.5)
        score -= over * 20

    if current > machine.current_warning:
        span = max(machine.current_critical - machine.current_warning, 1e-6)
        over = min((current - machine.current_warning) / span, 1.5)
        score -= over * 25

    if vibration > machine.vibration_warning:
        span = max(machine.vibration_critical - machine.vibration_warning, 1e-6)
        over = min((vibration - machine.vibration_warning) / span, 1.5)
        score -= over * 20

    return max(0.0, min(100.0, round(score, 1)))


def derive_status(machine: Machine, temperature: float, voltage: float, current: float, vibration: float) -> MachineStatus:
    voltage_dev = abs(voltage - machine.voltage_nominal)
    critical = (
        temperature >= machine.temp_critical
        or current >= machine.current_critical
        or vibration >= machine.vibration_critical
        or voltage_dev >= machine.voltage_tolerance * 2
    )
    if critical:
        return MachineStatus.CRITICAL

    warning = (
        temperature >= machine.temp_warning
        or current >= machine.current_warning
        or vibration >= machine.vibration_warning
        or voltage_dev >= machine.voltage_tolerance
    )
    if warning:
        return MachineStatus.WARNING

    return MachineStatus.NORMAL


async def ingest_sensor_reading(
    db: Session,
    machine: Machine,
    temperature: float,
    voltage: float,
    current: float,
    vibration: float,
):
    previous_status = machine.status

    machine.temperature = temperature
    machine.voltage = voltage
    machine.current = current
    machine.vibration = vibration
    machine.health_score = compute_health_score(machine, temperature, voltage, current, vibration)
    machine.status = derive_status(machine, temperature, voltage, current, vibration)

    reading = SensorReading(
        machine_id=machine.id,
        temperature=temperature,
        voltage=voltage,
        current=current,
        vibration=vibration,
    )
    db.add(reading)
    db.commit()
    db.refresh(machine)
    db.refresh(reading)

    # Only raise a *new* alert when the machine is crossing into a worse
    # state, not on every single reading while it stays WARNING/CRITICAL.
    if machine.status != previous_status and machine.status in (MachineStatus.WARNING, MachineStatus.CRITICAL):
        severity = AlertSeverity.CRITICAL if machine.status == MachineStatus.CRITICAL else AlertSeverity.WARNING

        if temperature >= machine.temp_warning:
            await alert_service.raise_alert(
                db, AlertType.HIGH_TEMPERATURE, severity,
                f"{machine.name} temperature at {temperature:.1f}\u00b0C",
                related_machine_id=machine.id,
            )
        if current >= machine.current_warning:
            await alert_service.raise_alert(
                db, AlertType.HIGH_CURRENT, severity,
                f"{machine.name} current at {current:.1f}A",
                related_machine_id=machine.id,
            )
        if vibration >= machine.vibration_warning:
            await alert_service.raise_alert(
                db, AlertType.HIGH_VIBRATION, severity,
                f"{machine.name} vibration at {vibration:.1f}mm/s",
                related_machine_id=machine.id,
            )
        if abs(voltage - machine.voltage_nominal) >= machine.voltage_tolerance:
            await alert_service.raise_alert(
                db, AlertType.HIGH_VOLTAGE, severity,
                f"{machine.name} voltage deviated to {voltage:.1f}V",
                related_machine_id=machine.id,
            )

    await manager.broadcast(
        "machine_update",
        {
            "id": machine.id,
            "machine_code": machine.machine_code,
            "name": machine.name,
            "status": machine.status.value,
            "temperature": machine.temperature,
            "voltage": machine.voltage,
            "current": machine.current,
            "vibration": machine.vibration,
            "health_score": machine.health_score,
            "is_running": machine.is_running,
        },
    )

    return reading
