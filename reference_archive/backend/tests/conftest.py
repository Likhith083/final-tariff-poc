import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import get_db, Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db):
    """Create a new database session for a test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create a test client with database session."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_hts_data():
    """Sample HTS data for testing."""
    return {
        "hts_code": "8471.30.01",
        "description": "Laptop computers, portable, weighing not more than 10 kg",
        "tariff_rate": 0.0,
        "country_origin": "US"
    }

@pytest.fixture
def sample_tariff_calculation():
    """Sample tariff calculation data for testing."""
    return {
        "hts_code": "8471.30.01",
        "country_origin": "US",
        "material_cost": 500.0,
        "currency": "USD",
        "freight_cost": 50.0,
        "insurance_cost": 10.0,
        "other_costs": 5.0
    }

@pytest.fixture
def sample_material_analysis():
    """Sample material analysis data for testing."""
    return {
        "material_composition": {
            "cotton": 80.0,
            "polyester": 20.0
        },
        "product_name": "Cotton T-Shirt",
        "current_cost": 10.0,
        "target_savings": 15.0
    }

@pytest.fixture
def sample_scenario():
    """Sample scenario data for testing."""
    return {
        "base_scenario": {
            "hts_code": "8471.30.01",
            "country": "China",
            "material_cost": 500.0
        },
        "changes": {
            "country": "Mexico"
        },
        "scenario_name": "Test Scenario"
    }

@pytest.fixture
def sample_chat_message():
    """Sample chat message data for testing."""
    return {
        "message": "What is the tariff rate for laptop computers?",
        "session_id": "test-session-123",
        "context_type": "hts"
    } 