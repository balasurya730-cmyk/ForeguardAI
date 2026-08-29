import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
import app.models  # noqa: F401
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool keeps a single shared connection alive for the whole in-memory
# SQLite database; without it every new connection would get its own blank
# database and tables created in setup would appear missing to the app.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    client.post("/api/auth/register", json={
        "full_name": "Test Admin",
        "email": "admin@test.com",
        "password": "Password@123",
        "role": "ADMIN",
    })
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Password@123"})
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
