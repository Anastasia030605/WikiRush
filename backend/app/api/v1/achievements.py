"""
Endpoints для достижений
"""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.achievement import (
    AchievementDetail,
    ShareAchievementRequest,
    ShareAchievementResponse,
    UserAchievementsList,
)
from app.services.achievement_service import achievement_service

router = APIRouter()


@router.get("/", response_model=UserAchievementsList)
async def get_user_achievements(
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Получение всех достижений пользователя

    Возвращает сетку достижений:
    - unlocked: полученные достижения (цветные иконки с датой получения)
    - locked: неполученные достижения (серые иконки с прогресс-баром)
    - total_points: общее количество набранных баллов
    """
    achievements_data = await achievement_service.get_user_achievements(
        db, current_user.id
    )

    return UserAchievementsList(
        unlocked=achievements_data["unlocked"],
        locked=achievements_data["locked"],
        total_points=achievements_data["total_points"],
    )


@router.get("/{achievement_id}", response_model=AchievementDetail)
async def get_achievement_detail(
    achievement_id: int,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Получение детальной информации о достижении

    При клике на конкретное достижение показывает:
    - Полное описание условия
    - История получения (дата и время)
    - Связанные достижения в цепочке
    - Статистика: процент игроков, получивших это достижение
    """
    achievement_data = await achievement_service.get_achievement_detail(
        db, achievement_id, current_user.id
    )

    if not achievement_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Достижение не найдено",
        )

    achievement = achievement_data["achievement"]

    return AchievementDetail(
        id=achievement.id,
        code=achievement.code,
        name=achievement.name,
        description=achievement.description,
        icon=achievement.icon,
        category=achievement.category,
        rarity=achievement.rarity,
        requirement=achievement.requirement,
        points=achievement.points,
        chain=achievement.chain,
        rarity_percentage=achievement_data["rarity_percentage"],
        created_at=achievement.created_at,
        related_achievements=achievement_data["related_achievements"],
    )


@router.post("/share", response_model=ShareAchievementResponse)
async def share_achievement(
    request: ShareAchievementRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Генерация карточки для шаринга достижения в соцсетях

    Возвращает:
    - Данные достижения
    - Имя пользователя
    - Дату получения
    - Процент редкости
    - Готовый текст для шаринга
    """
    share_data = await achievement_service.get_share_data(
        db, request.achievement_code, current_user.id
    )

    if not share_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Достижение не найдено или не получено",
        )

    return ShareAchievementResponse(**share_data)


@router.post("/check")
async def check_achievements(
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Проверка и выдача новых достижений

    Проверяет текущую статистику пользователя и выдает новые достижения,
    если условия выполнены. Возвращает список новых полученных достижений.
    """
    newly_granted = await achievement_service.check_and_grant_achievements(
        db, current_user.id
    )

    return {
        "newly_granted": [
            {
                "code": ach.code,
                "name": ach.name,
                "description": ach.description,
                "points": ach.points,
                "rarity": ach.rarity,
            }
            for ach in newly_granted
        ],
        "count": len(newly_granted),
    }
