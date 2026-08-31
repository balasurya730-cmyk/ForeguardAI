from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth import hash_password

db = SessionLocal()

users = [
    ('Worker', 'worker@forgeguard.ai', 'Worker@123', UserRole.OPERATOR),
    ('Manager', 'manager@forgeguard.ai', 'Manager@123', UserRole.MANAGER),
    ('MD', 'md@forgeguard.ai', 'Md@123', UserRole.ADMIN)
]

for name, email, pw, role in users:
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        u = User(full_name=name, email=email, hashed_password=hash_password(pw), role=role)
        db.add(u)

db.commit()
db.close()
print('Demo users seeded successfully.')
