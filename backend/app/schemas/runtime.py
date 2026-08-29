from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.runtime_session import RuntimeStatus


class RuntimeStartRequest(BaseModel):
    duration_seconds: int


class RuntimeSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    configured_seconds: int
    started_at: datetime
    stopped_at: Optional[datetime]
    status: RuntimeStatus


class RuntimeStatusOut(BaseModel):
    machine_id: int
    configured_seconds: int
    elapsed_seconds: int
    remaining_seconds: int
    status: str
