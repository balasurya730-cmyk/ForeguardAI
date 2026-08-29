import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class RuntimeStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class RuntimeSession(Base):
    __tablename__ = "runtime_sessions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)

    configured_seconds = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    status = Column(Enum(RuntimeStatus), default=RuntimeStatus.RUNNING)

    machine = relationship("Machine", back_populates="runtime_sessions")
