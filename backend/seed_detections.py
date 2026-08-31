from app.database import SessionLocal
from app.models.safety_event import SafetyEvent, ViolationType
import random
from datetime import datetime, timedelta

db = SessionLocal()

types = [
    ViolationType.HELMET, ViolationType.MASK, ViolationType.NO_HELMET,
    ViolationType.NO_MASK, ViolationType.NO_VEST, ViolationType.PERSON,
    ViolationType.SAFETY_CONE, ViolationType.VEST, ViolationType.MACHINERY,
    ViolationType.VEHICLE, ViolationType.SMOKING, ViolationType.PHONE
]

for i, vt in enumerate(types):
    event = SafetyEvent(
        worker_id=1,
        camera_id=1,
        violation_type=vt,
        confidence=random.uniform(0.8, 0.99),
        duration_seconds=random.uniform(1, 10),
        timestamp=datetime.utcnow() - timedelta(minutes=i)
    )
    db.add(event)

db.commit()
db.close()
print('Seeded all 12 detection types.')
