from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.machine import Machine, MachineStatus
from app.models.worker import Worker
from app.models.camera import Camera
from app.models.gas_zone import GasZone, GasZoneStatus
from app.models.alert import Alert, AlertStatus
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.schemas.safety import CameraOut
from app.auth import get_current_user

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    machines = db.query(Machine).all()
    online = [m for m in machines if m.status != MachineStatus.OFFLINE]
    avg_health = round(sum(m.health_score for m in machines) / len(machines), 1) if machines else 0.0

    workers_count = db.query(Worker).count()

    active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).all()
    safety_alerts = len(
        [a for a in active_alerts if a.alert_type.value in ("NO_HELMET", "NO_GLOVES", "NO_BOOTS", "NO_GLASSES", "NO_SAFETY_VEST", "MOBILE_PHONE")]
    )
    gas_alerts = len([a for a in active_alerts if a.alert_type.value in ("GAS_WARNING", "GAS_CRITICAL")])

    gas_zones = db.query(GasZone).all()

    recent_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(10).all()
    recent_violations = db.query(SafetyEvent).order_by(SafetyEvent.timestamp.desc()).limit(10).all()

    return {
        "machines_online": len(online),
        "machines_total": len(machines),
        "workers_monitored": workers_count,
        "average_machine_health": avg_health,
        "safety_alerts": safety_alerts,
        "gas_alerts": gas_alerts,
        "gas_zones_critical": len([z for z in gas_zones if z.status == GasZoneStatus.CRITICAL]),
        "recent_alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type.value,
                "severity": a.severity.value,
                "message": a.message,
                "status": a.status.value,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent_alerts
        ],
        "recent_violations": [
            {
                "id": v.id,
                "worker_id": v.worker_id,
                "violation_type": v.violation_type.value,
                "confidence": v.confidence,
                "timestamp": v.timestamp.isoformat(),
            }
            for v in recent_violations
        ],
    }


@router.get("/api/cameras", response_model=list[CameraOut])
def list_cameras(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Camera).order_by(Camera.id).all()
