import pytest
import asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool 
from src.database import User
from main import app
from src.database import Base, get_db
from src.auth import create_jwt_token
from datetime import datetime
from src.database import Link
import pytest_asyncio

# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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

# @pytest.fixture
# async def db_session():
#     """Фикстура для создания асинхронной сессии базы данных."""
#     engine = create_async_engine(TEST_DATABASE_URL, echo=True)
#     async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
#     # Создание всех таблиц в памяти
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
    
#     async with async_session() as session:
#         yield session

# @pytest.fixture
# async def test_user(db_session: AsyncSession):
#     """Фикстура для создания тестового пользователя."""
#     user = User(
#         username="testuser",
#         email="test@example.com",
#         hashed_password="hashed_password",
#     )
#     db_session.add(user)
#     await db_session.commit()
#     await db_session.refresh(user)
#     return user

# @pytest.fixture
# def jwt_token(test_user):
#     """Фикстура для создания JWT токена."""
#     return create_jwt_token(test_user.username)
