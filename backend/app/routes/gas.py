from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.gas_zone import GasZone
from app.models.user import User, UserRole
from app.schemas.gas import GasZoneOut, GasZoneCreate, GasZoneUpdate
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/gas", tags=["gas"])


@router.get("/zones", response_model=list[GasZoneOut])
def list_zones(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(GasZone).order_by(GasZone.id).all()


@router.get("/zones/{zone_id}", response_model=GasZoneOut)
def get_zone(zone_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    zone = db.query(GasZone).filter(GasZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Gas zone not found")
    return zone


@router.post("/zones", response_model=GasZoneOut, status_code=201)
def create_zone(
    payload: GasZoneCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    zone = GasZone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.put("/zones/{zone_id}", response_model=GasZoneOut)
def update_zone(
    zone_id: int,
    payload: GasZoneUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    zone = db.query(GasZone).filter(GasZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Gas zone not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    return zone
