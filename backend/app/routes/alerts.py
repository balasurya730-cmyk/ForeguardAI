from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert, AlertStatus
from app.models.user import User
from app.schemas.alert import AlertOut
from app.auth import get_current_user
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    status: AlertStatus | None = Query(default=None),
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()


@router.put("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge(alert_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    alert = alert_service.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}/resolve", response_model=AlertOut)
def resolve(alert_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    alert = alert_service.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
