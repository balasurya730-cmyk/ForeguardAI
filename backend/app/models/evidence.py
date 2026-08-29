from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    safety_event_id = Column(Integer, ForeignKey("safety_events.id"), nullable=True, index=True)

    image_path = Column(String(255), nullable=True)
    video_path = Column(String(255), nullable=True)

    event_type = Column(String(50), nullable=False)
    worker_id = Column(Integer, nullable=True)
    camera_id = Column(Integer, nullable=True)
    confidence = Column(Integer, default=0)  # stored as 0-100 for simple display

    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
