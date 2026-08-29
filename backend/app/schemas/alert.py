from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertType, AlertSeverity, AlertStatus


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    related_machine_id: Optional[int]
    related_worker_id: Optional[int]
    related_zone_id: Optional[int]
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
