"""
Pytest configuration and fixtures
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.achievement import Achievement
from app.models.user import User
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    # Короткий пароль для тестов
    test_password = "test123"

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash(test_password),
        is_active=True,
        total_games=0,
        total_wins=0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Сохраняем пароль как атрибут для использования в тестах
    user.plain_password = test_password

    return user


@pytest_asyncio.fixture
async def test_achievements(db_session: AsyncSession) -> list[Achievement]:
    """Create test achievements"""
    achievements_data = [
        {
            "code": "first_game",
            "name": "Первые шаги",
            "description": "Сыграйте свою первую игру в WikiRush",
            "icon": "🎮",
            "category": "games",
            "rarity": "common",
            "requirement": {"type": "games_played", "target": 1},
            "points": 10,
            "chain": ["first_game", "games_10"],
        },
        {
            "code": "games_10",
            "name": "Любитель",
            "description": "Сыграйте 10 игр",
            "icon": "🎯",
            "category": "games",
            "rarity": "common",
            "requirement": {"type": "games_played", "target": 10},
            "points": 25,
            "chain": ["first_game", "games_10"],
        },
        {
            "code": "first_win",
            "name": "Первая победа",
            "description": "Одержите свою первую победу",
            "icon": "🏆",
            "category": "wins",
            "rarity": "common",
            "requirement": {"type": "games_won", "target": 1},
            "points": 15,
            "chain": ["first_win", "wins_10"],
        },
        {
            "code": "wins_10",
            "name": "Победитель",
            "description": "Одержите 10 побед",
            "icon": "🥇",
            "category": "wins",
            "rarity": "common",
            "requirement": {"type": "games_won", "target": 10},
            "points": 30,
            "chain": ["first_win", "wins_10"],
        },
    ]

    achievements = []
    for ach_data in achievements_data:
        achievement = Achievement(**ach_data)
        db_session.add(achievement)
        achievements.append(achievement)

    await db_session.commit()
    return achievements


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User, test_achievements) -> dict[str, str]:
    """Get authentication headers"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": test_user.plain_password},
    )

    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
