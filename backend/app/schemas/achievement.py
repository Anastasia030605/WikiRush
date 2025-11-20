"""
Схемы для достижений
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AchievementBase(BaseModel):
    """Базовая схема достижения"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    icon: str | None
    category: str
    rarity: str
    requirement: dict
    points: int
    chain: list | None


class AchievementPublic(AchievementBase):
    """Публичная схема достижения"""

    pass


class AchievementWithStats(AchievementPublic):
    """Достижение со статистикой редкости"""

    rarity_percentage: float  # Процент игроков, получивших это достижение


class UserAchievementProgress(BaseModel):
    """Прогресс достижения пользователя"""

    model_config = ConfigDict(from_attributes=True)

    achievement: AchievementPublic
    progress: int  # Текущий прогресс
    is_unlocked: bool
    unlocked_at: datetime | None


class UserAchievementWithStats(UserAchievementProgress):
    """Достижение пользователя с полной статистикой"""

    rarity_percentage: float  # Редкость достижения
    target: int  # Целевое значение из requirement


class UserAchievementsList(BaseModel):
    """Список достижений пользователя с группировкой"""

    unlocked: list[UserAchievementWithStats]  # Полученные (цветные)
    locked: list[UserAchievementWithStats]  # Неполученные (серые + прогресс)
    total_points: int  # Общее количество набранных баллов


class AchievementDetail(AchievementWithStats):
    """Детальная информация о достижении"""

    created_at: datetime
    related_achievements: list[AchievementPublic] | None  # Связанные в цепочке


class ShareAchievementRequest(BaseModel):
    """Запрос на генерацию карточки для шаринга"""

    achievement_code: str


class ShareAchievementResponse(BaseModel):
    """Ответ с данными для карточки"""

    achievement: AchievementPublic
    unlocked_at: datetime
    user_name: str
    rarity_percentage: float
    share_text: str  # Готовый текст для шаринга
