"""
Скрипт для заполнения базы данных начальными достижениями
"""
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.achievement import Achievement


async def seed_achievements():
    """Создание начальных достижений"""
    achievements_data = [
        # Категория: Первые шаги
        {
            "code": "first_game",
            "name": "Первые шаги",
            "description": "Сыграйте свою первую игру в WikiRush",
            "icon": "🎮",
            "category": "games",
            "rarity": "common",
            "requirement": {"type": "games_played", "target": 1},
            "points": 10,
            "chain": ["first_game", "games_10", "games_50", "games_100"],
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
            "chain": ["first_game", "games_10", "games_50", "games_100"],
        },
        {
            "code": "games_50",
            "name": "Опытный игрок",
            "description": "Сыграйте 50 игр",
            "icon": "🏅",
            "category": "games",
            "rarity": "rare",
            "requirement": {"type": "games_played", "target": 50},
            "points": 50,
            "chain": ["first_game", "games_10", "games_50", "games_100"],
        },
        {
            "code": "games_100",
            "name": "Ветеран WikiRush",
            "description": "Сыграйте 100 игр",
            "icon": "👑",
            "category": "games",
            "rarity": "epic",
            "requirement": {"type": "games_played", "target": 100},
            "points": 100,
            "chain": ["first_game", "games_10", "games_50", "games_100"],
        },
        # Категория: Победы
        {
            "code": "first_win",
            "name": "Первая победа",
            "description": "Одержите свою первую победу",
            "icon": "🏆",
            "category": "wins",
            "rarity": "common",
            "requirement": {"type": "games_won", "target": 1},
            "points": 15,
            "chain": ["first_win", "wins_10", "wins_25", "wins_50", "wins_100"],
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
            "chain": ["first_win", "wins_10", "wins_25", "wins_50", "wins_100"],
        },
        {
            "code": "wins_25",
            "name": "Чемпион",
            "description": "Одержите 25 побед",
            "icon": "🥇",
            "category": "wins",
            "rarity": "rare",
            "requirement": {"type": "games_won", "target": 25},
            "points": 60,
            "chain": ["first_win", "wins_10", "wins_25", "wins_50", "wins_100"],
        },
        {
            "code": "wins_50",
            "name": "Мастер",
            "description": "Одержите 50 побед",
            "icon": "💎",
            "category": "wins",
            "rarity": "epic",
            "requirement": {"type": "games_won", "target": 50},
            "points": 120,
            "chain": ["first_win", "wins_10", "wins_25", "wins_50", "wins_100"],
        },
        {
            "code": "wins_100",
            "name": "Легенда WikiRush",
            "description": "Одержите 100 побед",
            "icon": "⭐",
            "category": "wins",
            "rarity": "legendary",
            "requirement": {"type": "games_won", "target": 100},
            "points": 250,
            "chain": ["first_win", "wins_10", "wins_25", "wins_50", "wins_100"],
        },
        # Категория: Скорость
        {
            "code": "speed_60",
            "name": "Быстрый старт",
            "description": "Победите менее чем за 60 секунд",
            "icon": "⚡",
            "category": "speed",
            "rarity": "rare",
            "requirement": {"type": "best_time", "target": 60},
            "points": 40,
            "chain": ["speed_60", "speed_30", "speed_15"],
        },
        {
            "code": "speed_30",
            "name": "Молния",
            "description": "Победите менее чем за 30 секунд",
            "icon": "⚡⚡",
            "category": "speed",
            "rarity": "epic",
            "requirement": {"type": "best_time", "target": 30},
            "points": 80,
            "chain": ["speed_60", "speed_30", "speed_15"],
        },
        {
            "code": "speed_15",
            "name": "Скорость света",
            "description": "Победите менее чем за 15 секунд",
            "icon": "⚡⚡⚡",
            "category": "speed",
            "rarity": "legendary",
            "requirement": {"type": "best_time", "target": 15},
            "points": 150,
            "chain": ["speed_60", "speed_30", "speed_15"],
        },
        # Категория: Эффективность (минимум переходов)
        {
            "code": "efficient_5",
            "name": "Эффективный путь",
            "description": "Победите, сделав не более 5 переходов",
            "icon": "🎯",
            "category": "efficiency",
            "rarity": "rare",
            "requirement": {"type": "best_steps", "target": 5},
            "points": 35,
            "chain": ["efficient_5", "efficient_3", "efficient_2"],
        },
        {
            "code": "efficient_3",
            "name": "Мастер навигации",
            "description": "Победите, сделав не более 3 переходов",
            "icon": "🧭",
            "category": "efficiency",
            "rarity": "epic",
            "requirement": {"type": "best_steps", "target": 3},
            "points": 70,
            "chain": ["efficient_5", "efficient_3", "efficient_2"],
        },
        {
            "code": "efficient_2",
            "name": "Кратчайший путь",
            "description": "Победите, сделав всего 2 перехода",
            "icon": "🎖️",
            "category": "efficiency",
            "rarity": "legendary",
            "requirement": {"type": "best_steps", "target": 2},
            "points": 200,
            "chain": ["efficient_5", "efficient_3", "efficient_2"],
        },
    ]

    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже достижения в базе
        result = await session.execute(select(Achievement))
        existing = result.scalars().all()

        if existing:
            print(f"В базе уже есть {len(existing)} достижений. Пропускаем инициализацию.")
            return

        # Создаем достижения
        for ach_data in achievements_data:
            achievement = Achievement(**ach_data)
            session.add(achievement)

        await session.commit()
        print(f"[OK] Создано {len(achievements_data)} достижений")


async def main():
    """Главная функция: создаем таблицы и заполняем данными"""
    print("[*] Создание таблиц БД...")
    await init_db()
    print("[*] Инициализация достижений...")
    await seed_achievements()
    print("[+] Готово!")


if __name__ == "__main__":
    asyncio.run(main())
