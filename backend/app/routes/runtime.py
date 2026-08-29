from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.machine import Machine
from app.models.user import User, UserRole
from app.schemas.runtime import RuntimeStartRequest, RuntimeStatusOut
from app.auth import get_current_user, require_roles
from app.services import runtime_service

router = APIRouter(prefix="/api/machines", tags=["runtime"])


@router.post("/{machine_id}/runtime/start", response_model=RuntimeStatusOut)
async def start_runtime(
    machine_id: int,
    payload: RuntimeStartRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    if payload.duration_seconds <= 0:
        raise HTTPException(status_code=400, detail="duration_seconds must be positive")

    await runtime_service.start_runtime(db, machine, payload.duration_seconds)
    return runtime_service.get_runtime_status(db, machine_id)


@router.post("/{machine_id}/runtime/stop", response_model=RuntimeStatusOut)
async def stop_runtime(
    machine_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    await runtime_service.stop_runtime(db, machine, completed=False)
    return runtime_service.get_runtime_status(db, machine_id)


@router.get("/{machine_id}/runtime", response_model=RuntimeStatusOut)
def get_runtime(machine_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return runtime_service.get_runtime_status(db, machine_id)
