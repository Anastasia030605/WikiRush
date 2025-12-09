"""
Endpoints для пользователей
"""
import os
import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DBSession
from app.models.achievement import UserAchievement
from app.schemas.achievement import UserAchievementResponse
from app.schemas.user import UserProfile, UserPublic, UserStats
from app.services.auth_service import auth_service

router = APIRouter()

# Директория для загрузки аватаров
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "avatars")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Допустимые типы файлов
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: CurrentUser,
):
    """Получение профиля текущего пользователя"""
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    db: DBSession,
):
    """Получение публичной информации о пользователе"""
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(
    user_id: int,
    db: DBSession,
):
    """Получение статистики пользователя"""
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    win_rate = (
        (user.total_wins / user.total_games * 100) if user.total_games > 0 else 0.0
    )

    return UserStats(
        total_games=user.total_games,
        total_wins=user.total_wins,
        win_rate=round(win_rate, 2),
        best_time=user.best_time,
        best_steps=user.best_steps,
        average_steps=None,  # TODO: calculate from game history
        average_time=None,  # TODO: calculate from game history
    )


@router.get("/{user_id}/achievements", response_model=List[UserAchievementResponse])
async def get_user_achievements(
    user_id: int,
    db: DBSession,
):
    """Получение достижений пользователя"""
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    # Получаем все достижения пользователя
    result = await db.execute(
        select(UserAchievement)
        .options(selectinload(UserAchievement.achievement))
        .where(UserAchievement.user_id == user_id)
        .order_by(UserAchievement.unlocked_at.desc())
    )
    user_achievements = result.scalars().all()

    return [
        UserAchievementResponse(
            id=ua.id,
            achievement_id=ua.achievement_id,
            achievement_name=ua.achievement.name,
            achievement_description=ua.achievement.description,
            achievement_icon=ua.achievement.icon,
            achievement_category=ua.achievement.category,
            achievement_points=ua.achievement.points,
            unlocked_at=ua.unlocked_at,
            progress=ua.progress,
        )
        for ua in user_achievements
    ]


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    """Загрузка аватара пользователя"""

    # Проверка типа файла
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Читаем файл
    contents = await file.read()
    file_size = len(contents)

    # Проверка размера файла
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает максимальный ({MAX_FILE_SIZE / 1024 / 1024}MB)",
        )

    # Генерируем уникальное имя файла
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Удаляем старый аватар если есть
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.split("/")[-1]
        old_file_path = os.path.join(UPLOAD_DIR, old_filename)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception as e:
                print(f"Failed to delete old avatar: {e}")

    # Сохраняем новый файл
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}",
        )

    # Обновляем URL аватара в базе данных
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(current_user)

    return {
        "message": "Аватар успешно загружен",
        "avatar_url": avatar_url,
    }
