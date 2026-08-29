from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.safety_event import SafetyEvent
from app.models.evidence import Evidence
from app.models.user import User
from app.schemas.safety import SafetyEventOut, SafetyEventCreate, EvidenceOut
from app.auth import get_current_user
from app.services import safety_service

router = APIRouter(tags=["safety"])


@router.get("/api/safety/events", response_model=list[SafetyEventOut])
def list_safety_events(
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(SafetyEvent).order_by(SafetyEvent.timestamp.desc()).limit(limit).all()


@router.get("/api/safety/events/{event_id}", response_model=SafetyEventOut)
def get_safety_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    event = db.query(SafetyEvent).filter(SafetyEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Safety event not found")
    return event


@router.post("/api/safety/events", response_model=SafetyEventOut, status_code=201)
async def create_safety_event(payload: SafetyEventCreate, db: Session = Depends(get_db)):
    """Used by the AI pipeline (ai/rules.py) once a violation clears the
    persistence rule; also usable for manual testing."""
    event = await safety_service.record_violation(
        db,
        worker_id=payload.worker_id,
        camera_id=payload.camera_id,
        violation_type=payload.violation_type,
        confidence=payload.confidence,
        duration_seconds=payload.duration_seconds,
        evidence_image_path=payload.evidence_path,
    )
    return event


@router.get("/api/evidence", response_model=list[EvidenceOut])
def list_evidence(limit: int = 100, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Evidence).order_by(Evidence.created_at.desc()).limit(limit).all()


@router.put("/api/evidence/{evidence_id}/reviewed", response_model=EvidenceOut)
def mark_evidence_reviewed(evidence_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    evidence.reviewed = True
    db.commit()
    db.refresh(evidence)
    return evidence
