"""
Turns a confirmed AI safety violation (already passed through the
persistence rule in ai/rules.py) into a SafetyEvent + Evidence row + Alert,
and broadcasts it to the dashboard.
"""
from sqlalchemy.orm import Session

from app.models.safety_event import SafetyEvent, ViolationType
from app.models.evidence import Evidence
from app.models.alert import AlertType, AlertSeverity
from app.services import alert_service
from app.websocket.manager import manager

_ALERT_TYPE_MAP = {
    ViolationType.NO_HELMET: AlertType.NO_HELMET,
    ViolationType.NO_PPE: AlertType.NO_PPE,
    ViolationType.MOBILE_USAGE: AlertType.MOBILE_USAGE,
}


async def record_violation(
    db: Session,
    worker_id: int | None,
    camera_id: int | None,
    violation_type: ViolationType,
    confidence: float,
    duration_seconds: float,
    evidence_image_path: str | None = None,
    evidence_video_path: str | None = None,
) -> SafetyEvent:
    event = SafetyEvent(
        worker_id=worker_id,
        camera_id=camera_id,
        violation_type=violation_type,
        confidence=confidence,
        duration_seconds=duration_seconds,
        evidence_path=evidence_image_path,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    evidence = Evidence(
        safety_event_id=event.id,
        image_path=evidence_image_path,
        video_path=evidence_video_path,
        event_type=violation_type.value,
        worker_id=worker_id,
        camera_id=camera_id,
        confidence=int(confidence * 100) if confidence <= 1 else int(confidence),
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    await manager.broadcast(
        "safety_event",
        {
            "id": event.id,
            "worker_id": event.worker_id,
            "camera_id": event.camera_id,
            "violation_type": event.violation_type.value,
            "confidence": event.confidence,
            "duration_seconds": event.duration_seconds,
            "evidence_path": event.evidence_path,
            "timestamp": event.timestamp.isoformat(),
        },
    )

    await alert_service.raise_alert(
        db,
        _ALERT_TYPE_MAP[violation_type],
        AlertSeverity.WARNING,
        f"{violation_type.value.replace('_', ' ').title()} detected"
        + (f" for worker #{worker_id}" if worker_id else ""),
        related_worker_id=worker_id,
    )

    return event
