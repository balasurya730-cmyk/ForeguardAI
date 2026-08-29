from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. C02
    name = Column(String(120), nullable=False)
    location = Column(String(120), nullable=True)
    stream_url = Column(String(255), nullable=True)  # RTSP/HTTP source, empty in demo mode
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
