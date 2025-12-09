"""
Сервис для работы с играми
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game, GameMode, GameParticipant, GameStatus
from app.models.user import User
from app.services.wikipedia_service import wikipedia_service


class GameService:
    """Сервис для работы с играми"""

    async def create_game(
        self,
        db: AsyncSession,
        creator_id: int,
        mode: GameMode,
        start_article: Optional[str],
        target_article: Optional[str],
        max_steps: int,
        time_limit: int,
        max_players: int,
    ) -> Game:
        """Создание новой игры"""
        # Проверяем количество незавершенных игр пользователя
        result = await db.execute(
            select(func.count())
            .select_from(Game)
            .where(
                Game.creator_id == creator_id,
                Game.status.in_([GameStatus.WAITING.value, GameStatus.IN_PROGRESS.value])
            )
        )
        active_games_count = result.scalar()

        if active_games_count >= 3:
            raise ValueError("Вы не можете создать более 3 незавершенных игр одновременно")

        # Генерируем случайные статьи если не указаны
        if not start_article:
            start_article = await wikipedia_service.get_random_article()
            if not start_article:
                raise ValueError("Не удалось получить случайную начальную статью")

        if not target_article:
            # Генерируем целевую статью, достижимую от начальной за 2-3 перехода
            import random

            depth = random.randint(2, 3)  # Глубина поиска 2-3 перехода

            max_attempts = 3
            for _ in range(max_attempts):
                target_article = await wikipedia_service.get_reachable_article_at_depth(
                    start_article, depth
                )
                if target_article and target_article != start_article:
                    break

            if not target_article or target_article == start_article:
                raise ValueError("Не удалось найти достижимую целевую статью")

        # Проверяем существование статей
        start_exists = await wikipedia_service.validate_article_exists(start_article)
        target_exists = await wikipedia_service.validate_article_exists(target_article)

        if not start_exists:
            raise ValueError(f"Статья '{start_article}' не найдена")

        if not target_exists:
            raise ValueError(f"Статья '{target_article}' не найдена")

        if start_article == target_article:
            raise ValueError("Начальная и целевая статьи не могут быть одинаковыми")

        game = Game(
            mode=mode.value,
            status=GameStatus.WAITING.value,
            start_article=start_article,
            target_article=target_article,
            max_steps=max_steps,
            time_limit=time_limit,
            max_players=max_players,
            creator_id=creator_id,
        )

        db.add(game)
        await db.commit()
        await db.refresh(game)

        # Автоматически присоединяем создателя
        await self.join_game(db, game.id, creator_id)

        return game

    async def get_game(self, db: AsyncSession, game_id: int) -> Optional[Game]:
        """Получение игры по ID"""
        result = await db.execute(
            select(Game)
            .options(
                selectinload(Game.creator),
                selectinload(Game.participants).selectinload(GameParticipant.user),
            )
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()

    async def list_games(
        self,
        db: AsyncSession,
        status: Optional[GameStatus] = None,
        mode: Optional[GameMode] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Game], int]:
        """Получение списка игр с фильтрацией по участию пользователя"""
        query = select(Game).options(
            selectinload(Game.creator), selectinload(Game.participants)
        )

        if status:
            query = query.where(Game.status == status.value)

        if mode:
            query = query.where(Game.mode == mode.value)

        # Фильтрация по участию пользователя
        # Всегда скрываем чужие одиночные игры
        if user_id is not None:
            from sqlalchemy import or_

            # Базовая фильтрация: показываем только мультиплеерные игры или свои одиночные
            base_filter = or_(
                Game.mode != GameMode.SINGLE.value,  # Все мультиплеерные игры
                Game.creator_id == user_id  # Или одиночные игры пользователя
            )

            # Для завершенных игр дополнительно фильтруем по участию
            if status and status.value in [GameStatus.FINISHED.value, GameStatus.CANCELLED.value]:
                query = query.join(GameParticipant).where(
                    GameParticipant.user_id == user_id,
                    base_filter
                )
            # Для активных игр просто применяем базовый фильтр
            else:
                query = query.where(base_filter)

        query = query.order_by(Game.created_at.desc())

        # Получаем общее количество
        count_query = select(func.count()).select_from(Game)
        if status:
            count_query = count_query.where(Game.status == status.value)
        if mode:
            count_query = count_query.where(Game.mode == mode.value)

        # Применяем ту же фильтрацию для подсчета
        if user_id is not None:
            from sqlalchemy import or_

            base_filter = or_(
                Game.mode != GameMode.SINGLE.value,
                Game.creator_id == user_id
            )

            if status and status.value in [GameStatus.FINISHED.value, GameStatus.CANCELLED.value]:
                count_query = count_query.join(GameParticipant).where(
                    GameParticipant.user_id == user_id,
                    base_filter
                )
            else:
                count_query = count_query.where(base_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Получаем игры с пагинацией
        result = await db.execute(query.offset(skip).limit(limit))
        games = list(result.scalars().all())

        return games, total or 0

    async def join_game(
        self, db: AsyncSession, game_id: int, user_id: int
    ) -> GameParticipant:
        """Присоединение к игре"""
        game = await self.get_game(db, game_id)

        if not game:
            raise ValueError("Игра не найдена")

        if game.status != GameStatus.WAITING.value:
            raise ValueError("Нельзя присоединиться к начатой или завершенной игре")

        # Проверяем, не присоединился ли уже
        existing = await db.execute(
            select(GameParticipant).where(
                GameParticipant.game_id == game_id, GameParticipant.user_id == user_id
            )
        )

        if existing.scalar_one_or_none():
            raise ValueError("Вы уже присоединились к этой игре")

        # Проверяем лимит игроков
        participants_count = len(game.participants)
        if participants_count >= game.max_players:
            raise ValueError("Игра заполнена")

        participant = GameParticipant(
            game_id=game_id,
            user_id=user_id,
            path=[game.start_article],
            current_article=game.start_article,
        )

        db.add(participant)
        await db.commit()
        await db.refresh(participant)

        return participant

    async def start_game(self, db: AsyncSession, game_id: int) -> Game:
        """Запуск игры"""
        game = await self.get_game(db, game_id)

        if not game:
            raise ValueError("Игра не найдена")

        if game.status != GameStatus.WAITING.value:
            raise ValueError("Игра уже начата или завершена")

        if len(game.participants) < 1:
            raise ValueError("В игре должен быть хотя бы один участник")

        game.status = GameStatus.IN_PROGRESS.value
        game.started_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(game)

        return game

    async def make_move(
        self, db: AsyncSession, game_id: int, user_id: int, article: str
    ) -> Tuple[GameParticipant, bool]:
        """
        Совершить ход (перейти на статью)
        Возвращает (participant, is_winner)
        """
        game = await self.get_game(db, game_id)

        if not game:
            raise ValueError("Игра не найдена")

        if game.status != GameStatus.IN_PROGRESS.value:
            raise ValueError("Игра не активна")

        # Находим участника
        result = await db.execute(
            select(GameParticipant).where(
                GameParticipant.game_id == game_id, GameParticipant.user_id == user_id
            )
        )
        participant = result.scalar_one_or_none()

        if not participant:
            raise ValueError("Вы не участвуете в этой игре")

        if participant.is_finished:
            raise ValueError("Вы уже завершили игру")

        # Проверяем лимит времени
        if not game.started_at:
            raise ValueError("Игра не начата")

        # Handle both timezone-aware and timezone-naive datetimes
        started_at = game.started_at
        if started_at.tzinfo is None:
            # Old games without timezone info - assume UTC
            started_at = started_at.replace(tzinfo=timezone.utc)

        time_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        if time_elapsed > game.time_limit:
            print(f"[DEBUG] Time limit exceeded for participant {user_id} in game {game_id}")
            # Время вышло - завершаем участника
            participant.is_finished = True
            participant.finished_at = datetime.now(timezone.utc)
            participant.time_taken = int(time_elapsed)

            # Обновляем total_games для пользователя
            user = await db.get(User, user_id)
            if user:
                user.total_games += 1

            # Сначала commit изменений участника
            await db.commit()
            await db.refresh(participant)
            await db.refresh(game)

            print(f"[DEBUG] After participant commit - is_finished={participant.is_finished}")

            # Затем проверяем, нужно ли завершить игру
            # Если одиночная игра, сразу завершаем игру
            if game.mode == GameMode.SINGLE.value:
                print(f"[DEBUG] Single player - finishing game")
                game.status = GameStatus.FINISHED.value
                game.finished_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(game)
            # Для мультиплеера проверяем, все ли финишировали
            else:
                all_finished = all(p.is_finished for p in game.participants)
                print(f"[DEBUG] Multiplayer - all_finished={all_finished}")
                if all_finished:
                    game.status = GameStatus.FINISHED.value
                    game.finished_at = datetime.now(timezone.utc)
                    # Обновляем total_games для всех участников
                    for p in game.participants:
                        u = await db.get(User, p.user_id)
                        if u:
                            u.total_games += 1
                    await db.commit()
                    await db.refresh(game)

            raise ValueError("Время вышло")

        # Проверяем лимит шагов (после хода будет steps_count + 1)
        if participant.steps_count >= game.max_steps:
            print(f"[DEBUG] Step limit exceeded for participant {user_id} in game {game_id}")
            # Лимит шагов превышен - завершаем участника
            participant.is_finished = True
            participant.finished_at = datetime.now(timezone.utc)
            participant.time_taken = int(time_elapsed)

            # Обновляем total_games для пользователя
            user = await db.get(User, user_id)
            if user:
                user.total_games += 1

            # Сначала commit изменений участника
            await db.commit()
            await db.refresh(participant)
            await db.refresh(game)

            print(f"[DEBUG] After participant commit - is_finished={participant.is_finished}")

            # Затем проверяем, нужно ли завершить игру
            # Если одиночная игра, сразу завершаем игру
            if game.mode == GameMode.SINGLE.value:
                print(f"[DEBUG] Single player - finishing game")
                game.status = GameStatus.FINISHED.value
                game.finished_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(game)
            # Для мультиплеера проверяем, все ли финишировали
            else:
                all_finished = all(p.is_finished for p in game.participants)
                print(f"[DEBUG] Multiplayer - all_finished={all_finished}")
                if all_finished:
                    game.status = GameStatus.FINISHED.value
                    game.finished_at = datetime.now(timezone.utc)
                    # Обновляем total_games для всех участников
                    for p in game.participants:
                        u = await db.get(User, p.user_id)
                        if u:
                            u.total_games += 1
                    await db.commit()
                    await db.refresh(game)

            raise ValueError("Превышен лимит шагов")

        # Проверяем что ссылка существует
        current = participant.current_article or game.start_article
        is_valid_link = await wikipedia_service.is_link_valid(current, article)

        if not is_valid_link:
            raise ValueError(f"Нет ссылки из '{current}' в '{article}'")

        # Совершаем ход
        participant.path.append(article)
        participant.current_article = article
        participant.steps_count += 1

        # Проверяем достижение цели
        is_winner = False
        if article == game.target_article:
            participant.is_finished = True
            participant.is_winner = True
            participant.finished_at = datetime.now(timezone.utc)
            participant.time_taken = int(time_elapsed)
            is_winner = True

            # Обновляем статистику пользователя
            user = await db.get(User, user_id)
            if user:
                user.total_games += 1  # Инкрементируем total_games при победе
                user.total_wins += 1
                if not user.best_time or participant.time_taken < user.best_time:
                    user.best_time = participant.time_taken
                if not user.best_steps or participant.steps_count < user.best_steps:
                    user.best_steps = participant.steps_count

        # Сначала commit всех изменений participant
        await db.commit()
        await db.refresh(participant)

        # Затем проверяем, нужно ли завершить игру
        if is_winner:
            # Перезагружаем игру с обновленными participants
            await db.refresh(game)

            print(f"[DEBUG] is_winner=True, game.mode={game.mode}, GameMode.SINGLE.value={GameMode.SINGLE.value}")
            print(f"[DEBUG] Comparison result: {game.mode == GameMode.SINGLE.value}")

            # Если это одиночная игра, сразу завершаем игру
            if game.mode == GameMode.SINGLE.value:
                print(f"[DEBUG] Setting game status to FINISHED")
                game.status = GameStatus.FINISHED.value
                game.finished_at = datetime.now(timezone.utc)
            # Для мультиплеера проверяем, все ли финишировали
            elif game.mode in [GameMode.MULTIPLAYER.value, GameMode.COOPERATIVE.value]:
                # Проверяем, все ли участники финишировали или превысили лимиты
                all_finished = all(p.is_finished for p in game.participants)
                if all_finished:
                    game.status = GameStatus.FINISHED.value
                    game.finished_at = datetime.now(timezone.utc)
                    # Обновляем total_games для всех участников
                    for p in game.participants:
                        u = await db.get(User, p.user_id)
                        if u:
                            u.total_games += 1

            # Commit изменений игры
            await db.commit()
            await db.refresh(game)

        # Проверяем и выдаем достижения после победы
        if is_winner:
            from app.services.achievement_service import achievement_service

            await achievement_service.check_and_grant_achievements(db, user_id)

        return participant, is_winner

    async def cancel_game(self, db: AsyncSession, game_id: int, user_id: int) -> Game:
        """Отмена игры (только создатель)"""
        game = await self.get_game(db, game_id)

        if not game:
            raise ValueError("Игра не найдена")

        if game.creator_id != user_id:
            raise ValueError("Только создатель может отменить игру")

        if game.status not in [GameStatus.WAITING.value, GameStatus.IN_PROGRESS.value]:
            raise ValueError("Игру можно отменить только если она не завершена")

        game.status = GameStatus.CANCELLED.value
        game.finished_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(game)

        return game

    async def finish_game(self, db: AsyncSession, game_id: int) -> Game:
        """Завершение игры"""
        game = await self.get_game(db, game_id)

        if not game:
            raise ValueError("Игра не найдена")

        game.status = GameStatus.FINISHED.value
        game.finished_at = datetime.now(timezone.utc)

        # Обновляем статистику только для участников, которые еще не были завершены
        # (чтобы избежать дублирования при повторных вызовах finish_game)
        from app.services.achievement_service import achievement_service

        for participant in game.participants:
            # Инкрементируем total_games только если участник еще не был завершен
            if not participant.is_finished:
                participant.is_finished = True
                participant.finished_at = datetime.now(timezone.utc)

                user = await db.get(User, participant.user_id)
                if user:
                    user.total_games += 1

        await db.commit()

        # Проверяем достижения для всех участников
        for participant in game.participants:
            await achievement_service.check_and_grant_achievements(
                db, participant.user_id
            )

        await db.refresh(game)

        return game

    async def get_leaderboard(self, db: AsyncSession, limit: int = 100) -> List[User]:
        """Получение таблицы лидеров"""
        result = await db.execute(
            select(User)
            .where(User.total_games > 0)
            .order_by(User.total_wins.desc(), User.best_time.asc())
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
game_service = GameService()

