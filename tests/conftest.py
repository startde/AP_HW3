import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool 
from main import app
from src.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def override_get_db():
    async with async_session() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="session")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def test_db():
    yield



@pytest.fixture()
async def client(init_db):
    async with AsyncClient(base_url="http://localhost:8000") as client: 
        app.router.lifespan_context(app) 
        yield client

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

