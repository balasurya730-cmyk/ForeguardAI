import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class MachineStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    location = Column(String(120), nullable=True)

    status = Column(Enum(MachineStatus), default=MachineStatus.NORMAL)

    temperature = Column(Float, default=0.0)
    voltage = Column(Float, default=0.0)
    current = Column(Float, default=0.0)
    vibration = Column(Float, default=0.0)
    health_score = Column(Float, default=100.0)

    # Thresholds used for health-score / alert calculation (configurable per machine)
    temp_warning = Column(Float, default=65.0)
    temp_critical = Column(Float, default=80.0)
    voltage_nominal = Column(Float, default=230.0)
    voltage_tolerance = Column(Float, default=10.0)
    current_warning = Column(Float, default=8.0)
    current_critical = Column(Float, default=12.0)
    vibration_warning = Column(Float, default=4.0)
    vibration_critical = Column(Float, default=7.0)

    is_running = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
    runtime_sessions = relationship("RuntimeSession", back_populates="machine", cascade="all, delete-orphan")
