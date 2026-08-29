import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from app.database import Base


class GasZoneStatus(str, enum.Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class GasZone(Base):
    __tablename__ = "gas_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(120), unique=True, nullable=False)
    gas_type = Column(String(50), default="LPG")  # configurable per zone/sensor

    current_ppm = Column(Float, default=0.0)
    warning_threshold = Column(Float, default=300.0)
    critical_threshold = Column(Float, default=600.0)

    status = Column(Enum(GasZoneStatus), default=GasZoneStatus.SAFE)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
