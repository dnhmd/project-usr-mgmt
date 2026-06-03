# tests/conftest.py

import bcrypt
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db.session import Base, get_db_session
from app.main import create_application
from app.models.domain import Role, User

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

def get_test_settings() -> Settings:
    """ Overide settings for testing. """

    return Settings(
        database_url=TEST_DATABASE_URL,
        debug=True,
        secret_key="test-secret-key",
    )

@pytest.fixture
async def test_engine():
    """ Create test database engine. """

    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """ Create test database session. """

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        # Seed roles
        session.add(Role(id=1, name="user"))
        session.add(Role(id=2, name="admin"))

        # Seed admin
        hashed = bcrypt.hashpw("adminpass123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        session.add(User(id=1, name="Super Admin", email="admin@app.com", hashed_password=hashed, is_active=True, role_id=2))
        await session.commit()

        yield session

@pytest.fixture
async def app(test_session):
    """ Create test application with overridden dependencies. """

    application = create_application()

    # Override settings
    application.dependency_overrides[get_settings] = get_test_settings

    # Override database session
    async def override_get_db():
        yield test_session
    
    application.dependency_overrides[get_db_session] = override_get_db

    yield application

    # Clear overrides
    application.dependency_overrides.clear()

@pytest.fixture
async def client(app):
    """ Create test HTTP client. """

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """ Create authorization headers for testing. """

    # In real tests, generate a valid test token
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
async def registered_user(client: AsyncClient):
    """ Create a registered user for testing. """

    await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "user@test.com",
            "password": "testpass123",
        }
    )
    
    return {"email": "user@test.com", "password": "testpass123"}

@pytest.fixture
async def user_token(client: AsyncClient, registered_user):
    """ Create access token for a user. """

    response = await client.post(
        "/api/v1/auth/login",
        json=registered_user
    )

    return response.json()["access_token"]

@pytest.fixture
async def admin_token(client: AsyncClient):
    """ Create access token for an admin. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@app.com",
            "password": "adminpass123",
        }
    )

    return response.json()["access_token"]