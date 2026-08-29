from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.worker import Worker
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.schemas.safety import WorkerOut, SafetyEventOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/workers", tags=["workers"])


@router.get("", response_model=list[WorkerOut])
def list_workers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Worker).order_by(Worker.id).all()


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(worker_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.get("/{worker_id}/events", response_model=list[SafetyEventOut])
def get_worker_events(worker_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(SafetyEvent)
        .filter(SafetyEvent.worker_id == worker_id)
        .order_by(SafetyEvent.timestamp.desc())
        .all()
    )
