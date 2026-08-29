import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OPERATOR, nullable=False)
    is_active = Column(Integer, default=1)  # 1 / 0 for SQLite<->MySQL portability
    created_at = Column(DateTime, default=datetime.utcnow)
