"""
Pydantic schemas
"""
from .achievement import (
    AchievementBase,
    AchievementDetail,
    AchievementPublic,
    AchievementWithStats,
    ShareAchievementRequest,
    ShareAchievementResponse,
    UserAchievementProgress,
    UserAchievementsList,
    UserAchievementWithStats,
)
from .auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    TokenPayload,
)
from .game import (
    GameCreate,
    GameDetail,
    GameJoinResponse,
    GameListResponse,
    GameMoveRequest,
    GameMoveResponse,
    GameParticipantDetail,
    GameParticipantPublic,
    GamePublic,
    GameUpdate,
)
from .user import (
    UserCreate,
    UserInDB,
    UserProfile,
    UserPublic,
    UserStats,
    UserUpdate,
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserPublic",
    "UserProfile",
    "UserStats",
    # Game
    "GameCreate",
    "GameUpdate",
    "GamePublic",
    "GameDetail",
    "GameParticipantPublic",
    "GameParticipantDetail",
    "GameJoinResponse",
    "GameMoveRequest",
    "GameMoveResponse",
    "GameListResponse",
    # Achievement
    "AchievementBase",
    "AchievementPublic",
    "AchievementWithStats",
    "AchievementDetail",
    "UserAchievementProgress",
    "UserAchievementWithStats",
    "UserAchievementsList",
    "ShareAchievementRequest",
    "ShareAchievementResponse",
]
