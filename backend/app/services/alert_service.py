"""
Centralized alert engine.

Every part of the system (sensor rules, safety rules, gas rules, runtime
completion) creates alerts through this single service so alert shape,
persistence and WebSocket broadcast stay consistent.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.websocket.manager import manager


async def raise_alert(
    db: Session,
    alert_type: AlertType,
    severity: AlertSeverity,
    message: str,
    related_machine_id: Optional[int] = None,
    related_worker_id: Optional[int] = None,
    related_zone_id: Optional[int] = None,
) -> Alert:
    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        message=message,
        related_machine_id=related_machine_id,
        related_worker_id=related_worker_id,
        related_zone_id=related_zone_id,
        status=AlertStatus.ACTIVE,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    await manager.broadcast(
        "alert",
        {
            "id": alert.id,
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "message": alert.message,
            "related_machine_id": alert.related_machine_id,
            "related_worker_id": alert.related_worker_id,
            "related_zone_id": alert.related_zone_id,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat(),
        },
    )
    return alert


def acknowledge_alert(db: Session, alert_id: int) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert
