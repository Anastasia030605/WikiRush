"""
Сервис для работы с достижениями
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.achievement import Achievement, UserAchievement
from app.models.user import User


class AchievementService:
    """Сервис для управления достижениями"""

    async def initialize_user_achievements(
        self, db: AsyncSession, user_id: int
    ) -> None:
        """
        Инициализация записей достижений для пользователя
        Создает UserAchievement для всех существующих достижений
        """
        # Получаем все достижения
        result = await db.execute(select(Achievement))
        achievements = result.scalars().all()

        # Проверяем, какие достижения уже есть у пользователя
        existing_result = await db.execute(
            select(UserAchievement.achievement_id).where(
                UserAchievement.user_id == user_id
            )
        )
        existing_ids = set(existing_result.scalars().all())

        # Создаем записи для недостающих достижений
        for achievement in achievements:
            if achievement.id not in existing_ids:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress=0,
                    is_unlocked=False,
                )
                db.add(user_achievement)

        await db.commit()

    async def check_and_grant_achievements(
        self, db: AsyncSession, user_id: int
    ) -> List[Achievement]:
        """
        Проверяет условия и выдает достижения пользователю
        Возвращает список новых полученных достижений
        """
        # Получаем пользователя с полной статистикой
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            return []

        # Получаем все достижения с прогрессом пользователя
        result = await db.execute(
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(
                UserAchievement.user_id == user_id, UserAchievement.is_unlocked == False
            )
        )
        user_achievements = result.scalars().all()

        newly_granted = []

        for ua in user_achievements:
            achievement = ua.achievement
            requirement = achievement.requirement
            req_type = requirement.get("type")
            target = requirement.get("target", 0)

            # Проверяем текущее значение статистики
            current_value = self._get_stat_value(user, req_type)

            # Обновляем прогресс
            ua.progress = min(current_value, target)

            # Проверяем, достигнута ли цель
            if current_value >= target:
                ua.is_unlocked = True
                ua.unlocked_at = datetime.now(timezone.utc)
                newly_granted.append(achievement)

        await db.commit()
        return newly_granted

    def _get_stat_value(self, user: User, stat_type: str) -> int:
        """Получить значение статистики пользователя по типу"""
        stat_mapping = {
            "games_played": user.total_games,
            "games_won": user.total_wins,
            "best_time": user.best_time or 999999,
            "best_steps": user.best_steps or 999999,
        }
        return stat_mapping.get(stat_type, 0)

    async def get_user_achievements(
        self, db: AsyncSession, user_id: int
    ) -> Dict[str, list]:
        """
        Получить все достижения пользователя с группировкой
        Возвращает словарь с unlocked и locked достижениями
        """
        # Инициализируем достижения для пользователя, если их нет
        await self.initialize_user_achievements(db, user_id)

        # Получаем все достижения пользователя
        result = await db.execute(
            select(UserAchievement)
            .options(selectinload(UserAchievement.achievement))
            .where(UserAchievement.user_id == user_id)
        )
        user_achievements = result.scalars().all()

        # Считаем общее количество пользователей для расчета редкости
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 1

        unlocked = []
        locked = []
        total_points = 0

        for ua in user_achievements:
            achievement = ua.achievement

            # Считаем процент получивших это достижение
            unlocked_count_result = await db.execute(
                select(func.count(UserAchievement.id)).where(
                    UserAchievement.achievement_id == achievement.id,
                    UserAchievement.is_unlocked == True,
                )
            )
            unlocked_count = unlocked_count_result.scalar() or 0
            rarity_percentage = (unlocked_count / total_users * 100) if total_users > 0 else 0

            achievement_data = {
                "achievement": achievement,
                "progress": ua.progress,
                "is_unlocked": ua.is_unlocked,
                "unlocked_at": ua.unlocked_at,
                "rarity_percentage": round(rarity_percentage, 2),
                "target": achievement.requirement.get("target", 0),
            }

            if ua.is_unlocked:
                unlocked.append(achievement_data)
                total_points += achievement.points
            else:
                locked.append(achievement_data)

        return {
            "unlocked": unlocked,
            "locked": locked,
            "total_points": total_points,
        }

    async def get_achievement_detail(
        self, db: AsyncSession, achievement_id: int, user_id: int
    ) -> Optional[dict]:
        """Получить детальную информацию о достижении"""
        # Получаем достижение
        ach_result = await db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = ach_result.scalar_one_or_none()

        if not achievement:
            return None

        # Получаем прогресс пользователя
        ua_result = await db.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
        )
        user_achievement = ua_result.scalar_one_or_none()

        # Считаем редкость
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 1

        unlocked_count_result = await db.execute(
            select(func.count(UserAchievement.id)).where(
                UserAchievement.achievement_id == achievement_id,
                UserAchievement.is_unlocked == True,
            )
        )
        unlocked_count = unlocked_count_result.scalar() or 0
        rarity_percentage = (unlocked_count / total_users * 100) if total_users > 0 else 0

        # Получаем связанные достижения из цепочки
        related_achievements = []
        if achievement.chain:
            related_result = await db.execute(
                select(Achievement).where(Achievement.code.in_(achievement.chain))
            )
            related_achievements = related_result.scalars().all()

        return {
            "achievement": achievement,
            "progress": user_achievement.progress if user_achievement else 0,
            "is_unlocked": user_achievement.is_unlocked if user_achievement else False,
            "unlocked_at": user_achievement.unlocked_at if user_achievement else None,
            "rarity_percentage": round(rarity_percentage, 2),
            "related_achievements": related_achievements,
        }

    async def get_share_data(
        self, db: AsyncSession, achievement_code: str, user_id: int
    ) -> Optional[dict]:
        """Получить данные для шаринга достижения"""
        # Получаем достижение по коду
        ach_result = await db.execute(
            select(Achievement).where(Achievement.code == achievement_code)
        )
        achievement = ach_result.scalar_one_or_none()

        if not achievement:
            return None

        # Получаем пользователя
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            return None

        # Получаем UserAchievement
        ua_result = await db.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id,
                UserAchievement.is_unlocked == True,
            )
        )
        user_achievement = ua_result.scalar_one_or_none()

        if not user_achievement:
            return None  # Нельзя поделиться неполученным достижением

        # Считаем редкость
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 1

        unlocked_count_result = await db.execute(
            select(func.count(UserAchievement.id)).where(
                UserAchievement.achievement_id == achievement.id,
                UserAchievement.is_unlocked == True,
            )
        )
        unlocked_count = unlocked_count_result.scalar() or 0
        rarity_percentage = (unlocked_count / total_users * 100) if total_users > 0 else 0

        # Формируем текст для шаринга
        share_text = (
            f"🏆 Я получил достижение '{achievement.name}' в WikiRush!\n"
            f"📊 Это достижение получили только {rarity_percentage:.1f}% игроков!\n"
            f"🎮 Присоединяйся к игре!"
        )

        return {
            "achievement": achievement,
            "unlocked_at": user_achievement.unlocked_at,
            "user_name": user.username,
            "rarity_percentage": round(rarity_percentage, 2),
            "share_text": share_text,
        }

    async def get_achievement_by_code(
        self, db: AsyncSession, code: str
    ) -> Optional[Achievement]:
        """Получить достижение по коду"""
        result = await db.execute(select(Achievement).where(Achievement.code == code))
        return result.scalar_one_or_none()


# Singleton instance
achievement_service = AchievementService()
