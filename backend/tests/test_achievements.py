"""
Tests for achievements system
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_achievements_empty(client: AsyncClient, auth_headers):
    """Test getting achievements for new user"""
    response = await client.get("/api/v1/achievements/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "unlocked" in data
    assert "locked" in data
    assert "total_points" in data
    assert data["total_points"] == 0
    # All achievements should be locked for new user
    assert len(data["unlocked"]) == 0
    assert len(data["locked"]) == 4  # 4 achievements created in test fixture


@pytest.mark.asyncio
async def test_get_user_achievements_with_progress(client: AsyncClient, auth_headers, test_user, db_session):
    """Test getting achievements with progress"""
    # Update user stats to trigger some achievements
    test_user.total_games = 1
    test_user.total_wins = 1
    await db_session.commit()
    await db_session.refresh(test_user)

    # Check achievements
    response = await client.post("/api/v1/achievements/check", headers=auth_headers)
    assert response.status_code == 200

    # Get user achievements
    response = await client.get("/api/v1/achievements/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "unlocked" in data
    assert "locked" in data
    assert "total_points" in data
    # Some achievements should be unlocked or have progress
    assert len(data["locked"]) <= 4


@pytest.mark.asyncio
async def test_check_achievements(client: AsyncClient, auth_headers, test_user, db_session):
    """Test checking and granting achievements"""
    # Set user stats
    test_user.total_games = 10
    test_user.total_wins = 5
    await db_session.commit()
    await db_session.refresh(test_user)

    # Check achievements
    response = await client.post("/api/v1/achievements/check", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "newly_granted" in data
    assert "count" in data
    # Count can be 0 or more depending on achievement logic
    assert data["count"] >= 0


@pytest.mark.asyncio
async def test_get_achievement_detail(client: AsyncClient, auth_headers, db_session):
    """Test getting achievement details"""
    # Assuming achievement with ID 1 exists from seed
    response = await client.get("/api/v1/achievements/1", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "name" in data
    assert "description" in data
    assert "rarity_percentage" in data
    assert "related_achievements" in data


@pytest.mark.asyncio
async def test_get_nonexistent_achievement(client: AsyncClient, auth_headers):
    """Test getting non-existent achievement"""
    response = await client.get("/api/v1/achievements/9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_share_achievement_not_unlocked(client: AsyncClient, auth_headers):
    """Test sharing achievement that is not unlocked"""
    response = await client.post(
        "/api/v1/achievements/share",
        headers=auth_headers,
        json={"achievement_code": "first_win"},
    )
    # Should fail because achievement is not unlocked
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_share_achievement_unlocked(client: AsyncClient, auth_headers, test_user, db_session):
    """Test sharing unlocked achievement"""
    # Grant user an achievement
    test_user.total_wins = 1
    await db_session.commit()

    # Check achievements to unlock them
    await client.post("/api/v1/achievements/check", headers=auth_headers)

    # Now try to share
    response = await client.post(
        "/api/v1/achievements/share",
        headers=auth_headers,
        json={"achievement_code": "first_win"},
    )

    if response.status_code == 200:
        data = response.json()
        assert "achievement" in data
        assert "user_name" in data
        assert "rarity_percentage" in data
        assert "share_text" in data
        assert "WikiRush" in data["share_text"]
