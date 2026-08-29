from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.gas_zone import GasZoneStatus


class GasZoneCreate(BaseModel):
    zone_name: str
    gas_type: str = "LPG"
    warning_threshold: float = 300.0
    critical_threshold: float = 600.0


class GasZoneUpdate(BaseModel):
    gas_type: Optional[str] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None


class GasZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_name: str
    gas_type: str
    current_ppm: float
    warning_threshold: float
    critical_threshold: float
    status: GasZoneStatus
    updated_at: datetime
