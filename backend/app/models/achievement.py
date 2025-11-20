"""
Модели достижений
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Achievement(Base):
    """Модель достижения"""

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Категория достижения (games, speed, wins, streaks, special)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="games")

    # Редкость (common, rare, epic, legendary)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False, default="common")

    # Условия получения (JSON с правилами)
    # Например: {"type": "games_won", "target": 10}
    # {"type": "speed_record", "target": 60}
    # {"type": "win_streak", "target": 5}
    requirement: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Баллы за достижение
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Связанные достижения (цепочка), например: ["first_win", "win_10", "win_50"]
    chain: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Achievement(code='{self.code}', name='{self.name}')>"


class UserAchievement(Base):
    """Модель связи пользователя и достижения"""

    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False
    )

    # Текущий прогресс пользователя (для неполученных достижений)
    # Например: 3 из 10 побед
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Флаг разблокировки
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    unlocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, unlocked={self.is_unlocked})>"
