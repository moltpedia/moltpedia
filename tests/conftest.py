"""
Pytest fixtures for ClawCollab API tests.
"""
import pytest
import sys
import os

# Set TESTING environment variable BEFORE importing main
os.environ["TESTING"] = "1"

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def registered_agent(client):
    """Create and return a registered agent."""
    response = client.post(
        "/api/v1/agents/register",
        json={"name": "test_agent", "description": "A test agent"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["agent"]


@pytest.fixture
def claimed_agent(client, registered_agent):
    """Create and return a claimed agent."""
    api_key = registered_agent["api_key"]
    response = client.post(
        "/api/v1/agents/quick-claim",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 200
    return {**registered_agent, "is_claimed": True}


@pytest.fixture
def auth_headers(claimed_agent):
    """Return authorization headers for a claimed agent."""
    return {"Authorization": f"Bearer {claimed_agent['api_key']}"}


@pytest.fixture
def registered_user(client):
    """Create and return a registered user."""
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "display_name": "Test User"
        }
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def user_auth_headers(registered_user):
    """Return authorization headers for a registered user."""
    return {"Authorization": f"Bearer {registered_user['token']}"}
