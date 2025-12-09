"""
Схемы для пользователей
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Схема создания пользователя"""

    password: str


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """Схема пользователя в БД"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    """Публичная схема пользователя (для других игроков)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    avatar_url: Optional[str] = None
    total_games: int
    total_wins: int
    best_time: Optional[int]
    best_steps: Optional[int]


class UserProfile(UserPublic):
    """Профиль пользователя (расширенная информация)"""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    created_at: datetime


class UserStats(BaseModel):
    """Статистика пользователя"""

    model_config = ConfigDict(from_attributes=True)

    total_games: int
    total_wins: int
    win_rate: float
    best_time: Optional[int]
    best_steps: Optional[int]
    average_steps: Optional[float]
    average_time: Optional[float]
