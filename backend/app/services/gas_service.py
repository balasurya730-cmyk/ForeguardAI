"""
Gas zone reading ingestion + threshold alerting.

Gas type, calibration and thresholds are configurable per zone
(GasZone.gas_type / warning_threshold / critical_threshold) rather than
hard-coded, since real deployments will use different sensors per gas.
"""
from sqlalchemy.orm import Session

from app.models.gas_zone import GasZone, GasZoneStatus
from app.models.alert import AlertType, AlertSeverity
from app.services import alert_service
from app.services.mqtt_service import publish_buzzer_command
from app.websocket.manager import manager


async def ingest_gas_reading(db: Session, zone: GasZone, ppm: float):
    previous_status = zone.status

    zone.current_ppm = ppm
    if ppm >= zone.critical_threshold:
        zone.status = GasZoneStatus.CRITICAL
    elif ppm >= zone.warning_threshold:
        zone.status = GasZoneStatus.WARNING
    else:
        zone.status = GasZoneStatus.SAFE

    db.commit()
    db.refresh(zone)

    if zone.status != previous_status:
        if zone.status == GasZoneStatus.CRITICAL:
            publish_buzzer_command(zone.zone_name, "ON")
            await alert_service.raise_alert(
                db, AlertType.GAS_CRITICAL, AlertSeverity.CRITICAL,
                f"{zone.zone_name} gas level CRITICAL at {ppm:.0f} ppm ({zone.gas_type})",
                related_zone_id=zone.id,
            )
        elif zone.status == GasZoneStatus.WARNING:
            await alert_service.raise_alert(
                db, AlertType.GAS_WARNING, AlertSeverity.WARNING,
                f"{zone.zone_name} gas level elevated at {ppm:.0f} ppm ({zone.gas_type})",
                related_zone_id=zone.id,
            )
        elif previous_status != GasZoneStatus.SAFE:
            publish_buzzer_command(zone.zone_name, "OFF")

    await manager.broadcast(
        "gas_update",
        {
            "id": zone.id,
            "zone_name": zone.zone_name,
            "gas_type": zone.gas_type,
            "current_ppm": zone.current_ppm,
            "warning_threshold": zone.warning_threshold,
            "critical_threshold": zone.critical_threshold,
            "status": zone.status.value,
        },
    )
    return zone
