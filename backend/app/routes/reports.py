from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.machine import Machine, MachineStatus
from app.models.safety_event import SafetyEvent
from app.models.gas_zone import GasZone, GasZoneStatus
from app.models.alert import Alert, AlertStatus
from app.models.runtime_session import RuntimeSession
from app.models.user import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _build_report(db: Session, since: datetime, period: str) -> dict:
    machines = db.query(Machine).all()
    avg_health = round(sum(m.health_score for m in machines) / len(machines), 1) if machines else 0.0
    downtime_machines = [m.machine_code for m in machines if m.status == MachineStatus.OFFLINE]

    safety_events = db.query(SafetyEvent).filter(SafetyEvent.timestamp >= since).all()
    violation_breakdown: dict[str, int] = {}
    for e in safety_events:
        violation_breakdown[e.violation_type.value] = violation_breakdown.get(e.violation_type.value, 0) + 1

    gas_incidents = (
        db.query(GasZone).filter(GasZone.status != GasZoneStatus.SAFE, GasZone.updated_at >= since).count()
    )

    alerts = db.query(Alert).filter(Alert.created_at >= since).all()
    alert_breakdown: dict[str, int] = {}
    for a in alerts:
        alert_breakdown[a.alert_type.value] = alert_breakdown.get(a.alert_type.value, 0) + 1

    sessions = db.query(RuntimeSession).filter(RuntimeSession.started_at >= since).all()
    total_runtime_seconds = sum(
        int(((s.stopped_at or datetime.utcnow()) - s.started_at).total_seconds()) for s in sessions
    )

    recommended_actions = []
    if avg_health < 80:
        recommended_actions.append("Schedule preventive maintenance for machines with declining health scores.")
    if any(violation_breakdown.get(h) for h in ["NO_HELMET", "NO_GLOVES", "NO_BOOTS", "NO_GLASSES", "NO_SAFETY_VEST"]):
        recommended_actions.append("Reinforce PPE protocols; multiple workers cited for missing gear.")
    if violation_breakdown.get("MOBILE_PHONE"):
        recommended_actions.append("Review mobile-phone policy enforcement in hazardous zones.")
    if gas_incidents:
        recommended_actions.append("Inspect gas sensors/ventilation in zones that crossed thresholds.")
    if not recommended_actions:
        recommended_actions.append("No significant risks detected in this period. Continue routine monitoring.")

    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "since": since.isoformat(),
        "machine_health_summary": {
            "average_health_score": avg_health,
            "machines_monitored": len(machines),
            "machines_offline": downtime_machines,
        },
        "safety_violations": violation_breakdown,
        "gas_incidents": gas_incidents,
        "alerts": alert_breakdown,
        "runtime_statistics": {
            "sessions": len(sessions),
            "total_runtime_seconds": total_runtime_seconds,
        },
        "recommended_actions": recommended_actions,
    }


@router.get("/daily")
def daily_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _build_report(db, datetime.utcnow() - timedelta(days=1), "daily")


@router.get("/weekly")
def weekly_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _build_report(db, datetime.utcnow() - timedelta(days=7), "weekly")


@router.get("/monthly")
def monthly_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _build_report(db, datetime.utcnow() - timedelta(days=30), "monthly")
