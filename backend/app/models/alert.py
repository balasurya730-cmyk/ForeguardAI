import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.database import Base


class AlertType(str, enum.Enum):
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    HIGH_VOLTAGE = "HIGH_VOLTAGE"
    HIGH_CURRENT = "HIGH_CURRENT"
    HIGH_VIBRATION = "HIGH_VIBRATION"
    NO_HELMET = "NO_HELMET"
    NO_GLOVES = "NO_GLOVES"
    NO_BOOTS = "NO_BOOTS"
    NO_GLASSES = "NO_GLASSES"
    NO_SAFETY_VEST = "NO_SAFETY_VEST"
    MOBILE_PHONE = "MOBILE_PHONE"
    GAS_WARNING = "GAS_WARNING"
    GAS_CRITICAL = "GAS_CRITICAL"
    MACHINE_RUNTIME_COMPLETE = "MACHINE_RUNTIME_COMPLETE"
    MACHINE_OFFLINE = "MACHINE_OFFLINE"


class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    message = Column(String(255), nullable=False)

    # Loosely-coupled references so one alert table can point at a machine, worker or zone.
    related_machine_id = Column(Integer, nullable=True)
    related_worker_id = Column(Integer, nullable=True)
    related_zone_id = Column(Integer, nullable=True)

    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
