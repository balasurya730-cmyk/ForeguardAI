from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.safety_event import ViolationType


class WorkerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    worker_code: str
    full_name: str
    department: Optional[str]
    shift: Optional[str]


class CameraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    camera_code: str
    name: str
    location: Optional[str]
    is_active: int


class SafetyEventCreate(BaseModel):
    worker_id: Optional[int] = None
    camera_id: Optional[int] = None
    violation_type: ViolationType
    confidence: float = 0.0
    duration_seconds: float = 0.0
    evidence_path: Optional[str] = None


class SafetyEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    worker_id: Optional[int]
    camera_id: Optional[int]
    violation_type: ViolationType
    confidence: float
    duration_seconds: float
    evidence_path: Optional[str]
    reviewed: bool
    timestamp: datetime


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    safety_event_id: Optional[int]
    image_path: Optional[str]
    video_path: Optional[str]
    event_type: str
    worker_id: Optional[int]
    camera_id: Optional[int]
    confidence: int
    reviewed: bool
    created_at: datetime
