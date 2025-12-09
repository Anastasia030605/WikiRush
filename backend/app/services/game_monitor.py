"""
Фоновый монитор для автоматического завершения игр с истекшим временем
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.game import Game, GameMode, GameParticipant, GameStatus
from app.models.user import User


class GameMonitor:
    """Монитор для проверки и завершения игр с истекшим временем"""

    def __init__(self):
        self.running = False
        self.check_interval = 5  # Проверяем каждые 5 секунд

    async def check_and_finish_expired_games(self, db: AsyncSession):
        """Проверяет и завершает игры с истекшим временем"""
        try:
            # Получаем все активные игры
            result = await db.execute(
                select(Game).where(Game.status == GameStatus.IN_PROGRESS.value)
            )
            games = result.scalars().all()

            for game in games:
                if not game.started_at:
                    continue

                # Handle both timezone-aware and timezone-naive datetimes
                started_at = game.started_at
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)

                time_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()

                # Если время истекло
                if time_elapsed > game.time_limit:
                    print(f"[MONITOR] Game {game.id} time limit exceeded ({time_elapsed}s > {game.time_limit}s)")

                    # Получаем участников
                    participants_result = await db.execute(
                        select(GameParticipant).where(GameParticipant.game_id == game.id)
                    )
                    participants = list(participants_result.scalars().all())

                    # Завершаем всех незавершенных участников
                    for participant in participants:
                        if not participant.is_finished:
                            participant.is_finished = True
                            participant.finished_at = datetime.now(timezone.utc)
                            participant.time_taken = int(time_elapsed)
                            print(f"[MONITOR] Marking participant {participant.user_id} as finished")

                            # Обновляем total_games только для тех, кто НЕ был завершен
                            user = await db.get(User, participant.user_id)
                            if user:
                                user.total_games += 1

                    # Завершаем игру
                    game.status = GameStatus.FINISHED.value
                    game.finished_at = datetime.now(timezone.utc)

                    await db.commit()
                    print(f"[MONITOR] Game {game.id} finished due to timeout")

        except Exception as e:
            print(f"[MONITOR] Error checking games: {e}")
            await db.rollback()

    async def start(self):
        """Запускает фоновую задачу мониторинга"""
        self.running = True
        print("[MONITOR] Game monitor started")

        while self.running:
            try:
                async with AsyncSessionLocal() as db:
                    await self.check_and_finish_expired_games(db)
            except Exception as e:
                print(f"[MONITOR] Error in monitor loop: {e}")

            # Ждем перед следующей проверкой
            await asyncio.sleep(self.check_interval)

    async def stop(self):
        """Останавливает фоновую задачу"""
        self.running = False
        print("[MONITOR] Game monitor stopped")


# Singleton instance
game_monitor = GameMonitor()
