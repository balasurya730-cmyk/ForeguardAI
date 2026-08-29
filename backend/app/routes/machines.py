from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.models.gas_zone import GasZone
from app.models.user import User, UserRole
from app.schemas.machine import MachineCreate, MachineUpdate, MachineOut, SensorReadingOut, SensorDataIn
from app.auth import get_current_user, require_roles
from app.services import machine_service
from app.services.gas_service import ingest_gas_reading

router = APIRouter(tags=["machines"])


@router.get("/api/machines", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Machine).order_by(Machine.id).all()


@router.get("/api/machines/{machine_id}", response_model=MachineOut)
def get_machine(machine_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@router.post("/api/machines", response_model=MachineOut, status_code=201)
def create_machine(
    payload: MachineCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    if db.query(Machine).filter(Machine.machine_code == payload.machine_code).first():
        raise HTTPException(status_code=400, detail="A machine with this code already exists")
    machine = Machine(**payload.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@router.put("/api/machines/{machine_id}", response_model=MachineOut)
def update_machine(
    machine_id: int,
    payload: MachineUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/api/machines/{machine_id}", status_code=204)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
    return None


@router.get("/api/machines/{machine_id}/readings", response_model=list[SensorReadingOut])
def get_machine_readings(
    machine_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.recorded_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/api/sensors/data", status_code=202)
async def post_sensor_data(payload: SensorDataIn, db: Session = Depends(get_db)):
    """Ingestion endpoint for real ESP32 devices that prefer HTTP POST over
    MQTT, or for manual testing (e.g. curl / Postman) without a broker."""
    machine = db.query(Machine).filter(Machine.machine_code == payload.machine_code).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Unknown machine_code")

    await machine_service.ingest_sensor_reading(
        db, machine, payload.temperature, payload.voltage, payload.current, payload.vibration
    )

    if payload.gas_ppm is not None and payload.zone_name:
        zone = db.query(GasZone).filter(GasZone.zone_name == payload.zone_name).first()
        if zone:
            await ingest_gas_reading(db, zone, payload.gas_ppm)

    return {"status": "accepted"}
