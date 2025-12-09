"""
Схемы для достижений
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AchievementBase(BaseModel):
    """Базовая схема достижения"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    icon: Optional[str]
    category: str
    rarity: str
    requirement: dict
    points: int
    chain: Optional[list]


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
    unlocked_at: Optional[datetime]


class UserAchievementWithStats(UserAchievementProgress):
    """Достижение пользователя с полной статистикой"""

    rarity_percentage: float  # Редкость достижения
    target: int  # Целевое значение из requirement


class UserAchievementsList(BaseModel):
    """Список достижений пользователя с группировкой"""

    unlocked: List[UserAchievementWithStats]  # Полученные (цветные)
    locked: List[UserAchievementWithStats]  # Неполученные (серые + прогресс)
    total_points: int  # Общее количество набранных баллов


class AchievementDetail(AchievementWithStats):
    """Детальная информация о достижении"""

    created_at: datetime
    related_achievements: Optional[List[AchievementPublic]]  # Связанные в цепочке


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


class UserAchievementResponse(BaseModel):
    """Достижение пользователя для профиля"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    achievement_id: int
    achievement_name: str
    achievement_description: str
    achievement_icon: Optional[str]
    achievement_category: str
    achievement_points: int
    unlocked_at: datetime
    progress: int
