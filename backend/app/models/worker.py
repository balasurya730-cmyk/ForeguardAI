from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    worker_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. WORKER-08
    full_name = Column(String(120), nullable=False)
    department = Column(String(120), nullable=True)
    shift = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
