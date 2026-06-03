# tests/conftest.py

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db.session import Base, get_db_session
from app.main import create_application

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