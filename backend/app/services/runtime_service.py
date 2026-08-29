"""
Machine runtime automation.

Flow: Manager -> FastAPI -> MQTT -> ESP32 -> Relay

start_runtime()/stop_runtime() persist a RuntimeSession and publish a
relay command over MQTT (a no-op log line in DEMO mode). A background
asyncio task (started in main.py) polls running sessions once a second
and automatically stops any machine whose configured duration has
elapsed, raising a MACHINE_RUNTIME_COMPLETE alert.
"""
import asyncio
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.runtime_session import RuntimeSession, RuntimeStatus
from app.models.alert import AlertType, AlertSeverity
from app.services import alert_service
from app.services.mqtt_service import publish_relay_command
from app.websocket.manager import manager


def get_active_session(db: Session, machine_id: int) -> RuntimeSession | None:
    return (
        db.query(RuntimeSession)
        .filter(RuntimeSession.machine_id == machine_id, RuntimeSession.status == RuntimeStatus.RUNNING)
        .order_by(RuntimeSession.id.desc())
        .first()
    )


async def start_runtime(db: Session, machine: Machine, duration_seconds: int) -> RuntimeSession:
    existing = get_active_session(db, machine.id)
    if existing:
        existing.status = RuntimeStatus.STOPPED
        existing.stopped_at = datetime.utcnow()

    session = RuntimeSession(
        machine_id=machine.id,
        configured_seconds=duration_seconds,
        started_at=datetime.utcnow(),
        status=RuntimeStatus.RUNNING,
    )
    machine.is_running = 1
    db.add(session)
    db.commit()
    db.refresh(session)

    publish_relay_command(machine.machine_code, "ON")

    await manager.broadcast(
        "runtime_update",
        _session_payload(session, elapsed=0, remaining=duration_seconds),
    )
    return session


async def stop_runtime(db: Session, machine: Machine, completed: bool = False) -> RuntimeSession | None:
    session = get_active_session(db, machine.id)
    if not session:
        return None

    session.status = RuntimeStatus.COMPLETED if completed else RuntimeStatus.STOPPED
    session.stopped_at = datetime.utcnow()
    machine.is_running = 0
    db.commit()
    db.refresh(session)

    publish_relay_command(machine.machine_code, "OFF")

    elapsed = int((session.stopped_at - session.started_at).total_seconds())
    await manager.broadcast(
        "runtime_update",
        _session_payload(session, elapsed=elapsed, remaining=0),
    )

    if completed:
        await alert_service.raise_alert(
            db,
            AlertType.MACHINE_RUNTIME_COMPLETE,
            AlertSeverity.INFO,
            f"{machine.name} completed its configured runtime and was stopped automatically.",
            related_machine_id=machine.id,
        )
    return session


def get_runtime_status(db: Session, machine_id: int) -> dict:
    session = get_active_session(db, machine_id)
    if not session:
        return {
            "machine_id": machine_id,
            "configured_seconds": 0,
            "elapsed_seconds": 0,
            "remaining_seconds": 0,
            "status": "STOPPED",
        }
    elapsed = int((datetime.utcnow() - session.started_at).total_seconds())
    remaining = max(0, session.configured_seconds - elapsed)
    return {
        "machine_id": machine_id,
        "configured_seconds": session.configured_seconds,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
        "status": session.status.value,
    }


def _session_payload(session: RuntimeSession, elapsed: int, remaining: int) -> dict:
    return {
        "machine_id": session.machine_id,
        "configured_seconds": session.configured_seconds,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
        "status": session.status.value,
    }


async def runtime_monitor_loop(session_factory):
    """Background task: every second, auto-stop machines whose runtime elapsed."""
    while True:
        db = session_factory()
        try:
            running = db.query(RuntimeSession).filter(RuntimeSession.status == RuntimeStatus.RUNNING).all()
            for session in running:
                elapsed = (datetime.utcnow() - session.started_at).total_seconds()
                if elapsed >= session.configured_seconds:
                    machine = db.query(Machine).filter(Machine.id == session.machine_id).first()
                    if machine:
                        await stop_runtime(db, machine, completed=True)
        finally:
            db.close()
        await asyncio.sleep(1)
