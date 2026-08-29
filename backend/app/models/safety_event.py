import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from app.database import Base


class ViolationType(str, enum.Enum):
    NO_HELMET = "NO_HELMET"
    NO_PPE = "NO_PPE"
    MOBILE_USAGE = "MOBILE_USAGE"


class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True, index=True)

    violation_type = Column(Enum(ViolationType), nullable=False)
    confidence = Column(Float, default=0.0)
    duration_seconds = Column(Float, default=0.0)

    evidence_path = Column(String(255), nullable=True)
    reviewed = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
