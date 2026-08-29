from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)

    temperature = Column(Float)
    voltage = Column(Float)
    current = Column(Float)
    vibration = Column(Float)

    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    machine = relationship("Machine", back_populates="readings")
