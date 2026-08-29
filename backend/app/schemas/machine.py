from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.machine import MachineStatus


class MachineCreate(BaseModel):
    machine_code: str
    name: str
    location: Optional[str] = None
    temp_warning: float = 65.0
    temp_critical: float = 80.0
    voltage_nominal: float = 230.0
    voltage_tolerance: float = 10.0
    current_warning: float = 8.0
    current_critical: float = 12.0
    vibration_warning: float = 4.0
    vibration_critical: float = 7.0


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    temp_warning: Optional[float] = None
    temp_critical: Optional[float] = None
    voltage_nominal: Optional[float] = None
    voltage_tolerance: Optional[float] = None
    current_warning: Optional[float] = None
    current_critical: Optional[float] = None
    vibration_warning: Optional[float] = None
    vibration_critical: Optional[float] = None


class MachineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_code: str
    name: str
    location: Optional[str]
    status: MachineStatus
    temperature: float
    voltage: float
    current: float
    vibration: float
    health_score: float
    is_running: int
    updated_at: datetime


class SensorReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    temperature: float
    voltage: float
    current: float
    vibration: float
    recorded_at: datetime


class SensorDataIn(BaseModel):
    """Payload shape ESP32 (or the demo simulator) posts to /api/sensors/data"""
    machine_code: str
    temperature: float
    voltage: float
    current: float
    vibration: float
    gas_ppm: Optional[float] = None
    zone_name: Optional[str] = None
