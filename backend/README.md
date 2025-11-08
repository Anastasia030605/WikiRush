# WikiRush Backend

FastAPI backend для игры WikiRush - гонки по Википедии.

## Особенности

- FastAPI с async/await
- SQLAlchemy 2.0 с async поддержкой
- SQLite для разработки (PostgreSQL для production)
- JWT аутентификация
- WebSocket для real-time обновлений
- Интеграция с Wikipedia API (русская Википедия)
- Автоматическая генерация случайных статей с гарантированным путём
- Полное покрытие типами (mypy)
- Линтеры и форматтеры (ruff, black)
- Pre-commit hooks
- Pytest с async тестами

## Установка

### Требования

- Python 3.11 или 3.12 (Python 3.13 не поддерживается из-за зависимостей)
- SQLite (уже включен в Python)
- PostgreSQL 15+ (опционально, для production)

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/wikirush.git
cd wikirush/backend
```

2. Создайте виртуальное окружение:
```bash
# Рекомендуется Python 3.11
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и настройте переменные:
```bash
# Для разработки можно использовать SQLite (по умолчанию)
DATABASE_URL=sqlite+aiosqlite:///./wikirush.db

# Wikipedia API (русская Википедия)
WIKIPEDIA_API_URL=https://ru.wikipedia.org/w/api.php
WIKIPEDIA_RATE_LIMIT=10

# JWT секреты
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

5. База данных будет создана автоматически при первом запуске

## Запуск

### Для разработки

```bash
# Из директории backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или через Python модуль:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### С помощью Docker (если настроен)

```bash
cd ..  # В корень проекта
docker-compose up
```

## API Документация

После запуска доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py           # Зависимости (DB, auth)
│   │   └── v1/
│   │       ├── __init__.py   # API router
│   │       ├── auth.py       # Аутентификация
│   │       ├── games.py      # Игры
│   │       ├── leaderboard.py # Лидерборд
│   │       ├── users.py      # Пользователи
│   │       └── wikipedia.py  # Wikipedia API
│   ├── core/
│   │   ├── config.py         # Конфигурация
│   │   ├── database.py       # Подключение к БД
│   │   └── security.py       # JWT, хеширование
│   ├── models/
│   │   ├── game.py           # Модели игр
│   │   └── user.py           # Модели пользователей
│   ├── schemas/
│   │   ├── game.py           # Pydantic схемы игр
│   │   └── user.py           # Pydantic схемы пользователей
│   ├── services/
│   │   ├── game_service.py       # Логика игр
│   │   ├── websocket_service.py  # WebSocket менеджер
│   │   └── wikipedia_service.py  # Wikipedia API клиент
│   └── main.py               # Точка входа
├── tests/
│   ├── conftest.py           # Pytest конфигурация
│   └── ...                   # Тесты
├── .env                      # Переменные окружения (создать вручную)
├── requirements.txt          # Зависимости
└── README.md
```

## Основные эндпоинты

### Аутентификация (`/api/v1/auth`)
- `POST /register` - Регистрация нового пользователя
- `POST /login` - Вход (получение access и refresh токенов)
- `POST /refresh` - Обновление access токена

### Пользователи (`/api/v1/users`)
- `GET /me` - Информация о текущем пользователе
- `GET /{id}` - Информация о пользователе по ID
- `GET /{id}/stats` - Статистика пользователя

### Игры (`/api/v1/games`)
- `POST /` - Создать новую игру
- `GET /` - Список всех игр (с фильтрацией и пагинацией)
- `GET /random-articles` - Получить случайные начальную и целевую статьи с гарантированным путём
- `GET /{id}` - Информация об игре
- `GET /{id}/available-links` - Доступные ссылки из текущей позиции игрока
- `POST /{id}/join` - Присоединиться к игре
- `POST /{id}/start` - Запустить игру (только создатель)
- `POST /{id}/move` - Сделать ход (перейти на другую статью)
- `WS /{id}/ws` - WebSocket соединение для real-time обновлений

### Wikipedia (`/api/v1/wikipedia`)
- `GET /article/{title}/summary` - Краткое описание статьи
- `GET /article/{title}/links` - Список ссылок из статьи
- `GET /search` - Поиск статей по запросу

### Лидерборд (`/api/v1/leaderboard`)
- `GET /` - Таблица лидеров

## Ключевые возможности

### Случайные статьи с гарантированным путём

Система автоматически генерирует начальную и целевую статьи так, чтобы между ними существовал путь длиной 2-3 перехода. Это реализовано через метод `get_reachable_article_at_depth()` в `wikipedia_service.py`.

```python
# Пример использования эндпоинта
GET /api/v1/games/random-articles

# Ответ:
{
  "start_article": "Москва",
  "target_article": "Кремль",
  "min_steps": 2
}
```

### Просмотр доступных ссылок

Игроки могут просматривать все доступные ссылки из своей текущей позиции:

```python
GET /api/v1/games/{game_id}/available-links

# Ответ:
{
  "current_article": "Москва",
  "target_article": "Кремль",
  "available_links": ["Россия", "История", "География", ...],
  "total_links": 50
}
```

### Real-time обновления через WebSocket

WebSocket соединение обеспечивает:
- Уведомления о присоединении игроков
- Уведомления о ходах других игроков
- Уведомления о победе
- Обновления статуса игры

## Тестирование

Запуск всех тестов:
```bash
pytest
```

С покрытием кода:
```bash
pytest --cov=app --cov-report=html
```

Запуск конкретного теста:
```bash
pytest tests/test_auth.py -v
```

## Линтинг и форматирование

```bash
# Форматирование кода
black .

# Линтинг
ruff check .

# Исправление проблем линтера
ruff check --fix .

# Проверка типов
mypy app/

# Все проверки сразу (через pre-commit)
pre-commit run --all-files
```

## Разработка

### Добавление новых зависимостей

```bash
pip install package_name
pip freeze > requirements.txt
```

### Работа с базой данных

По умолчанию используется SQLite. База создается автоматически при первом запуске.

Для очистки базы данных:
```bash
# Из директории backend
rm wikirush.db
# База будет создана заново при следующем запуске
```

Для использования PostgreSQL в production:
```bash
# В .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/wikirush
```

### Миграции (с Alembic, если настроены)

```bash
# Создать миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

## Примеры использования API

### Регистрация и вход

```python
import httpx

# Регистрация
response = httpx.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "player1",
        "email": "player1@example.com",
        "password": "secure_password"
    }
)

# Вход
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "player1",
        "password": "secure_password"
    }
)
token_data = response.json()
access_token = token_data["access_token"]

# Использование токена
headers = {"Authorization": f"Bearer {access_token}"}
```

### Создание игры со случайными статьями

```python
# Создание игры с автоматически выбранными статьями
response = httpx.post(
    "http://localhost:8000/api/v1/games",
    headers=headers,
    json={
        "mode": "single",
        # start_article и target_article можно не указывать
        # они будут выбраны автоматически
        "max_steps": 50,
        "time_limit": 300,
        "max_players": 1
    }
)
game = response.json()
print(f"Игра создана: от {game['start_article']} до {game['target_article']}")
```

### Создание игры с конкретными статьями

```python
response = httpx.post(
    "http://localhost:8000/api/v1/games",
    headers=headers,
    json={
        "mode": "multiplayer",
        "start_article": "Москва",
        "target_article": "Санкт-Петербург",
        "max_steps": 100,
        "time_limit": 600,
        "max_players": 5
    }
)
```

### Получение случайных статей

```python
# Получить предложение случайных статей перед созданием игры
response = httpx.get("http://localhost:8000/api/v1/games/random-articles")
articles = response.json()
print(f"Предложенный маршрут: {articles['start_article']} -> {articles['target_article']}")
print(f"Минимум шагов: {articles['min_steps']}")
```

### Игровой процесс

```python
# Присоединиться к игре
game_id = 1
response = httpx.post(
    f"http://localhost:8000/api/v1/games/{game_id}/join",
    headers=headers
)

# Запустить игру (только создатель)
response = httpx.post(
    f"http://localhost:8000/api/v1/games/{game_id}/start",
    headers=headers
)

# Получить доступные ссылки
response = httpx.get(
    f"http://localhost:8000/api/v1/games/{game_id}/available-links",
    headers=headers
)
links = response.json()["available_links"]

# Сделать ход
response = httpx.post(
    f"http://localhost:8000/api/v1/games/{game_id}/move",
    headers=headers,
    json={"article": links[0]}  # Переход на первую доступную ссылку
)
move_result = response.json()
if move_result["is_target_reached"]:
    print("Победа!")
```

### Получение информации о статье

```python
# Краткое описание статьи
response = httpx.get(
    "http://localhost:8000/api/v1/wikipedia/article/Москва/summary"
)
summary = response.json()
print(summary["extract"])  # Краткое описание

# Ссылки из статьи
response = httpx.get(
    "http://localhost:8000/api/v1/wikipedia/article/Москва/links?limit=20"
)
links = response.json()["links"]

# Поиск статей
response = httpx.get(
    "http://localhost:8000/api/v1/wikipedia/search?query=космос&limit=10"
)
results = response.json()["results"]
```

## Troubleshooting

### База данных не подключается

Для SQLite проверьте, что путь в `.env` правильный:
```bash
DATABASE_URL=sqlite+aiosqlite:///./wikirush.db
```

Для PostgreSQL проверьте настройки:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wikirush
```

### Wikipedia API не отвечает

Проверьте:
1. Доступ к интернету
2. URL в `.env`:
```bash
WIKIPEDIA_API_URL=https://ru.wikipedia.org/w/api.php
```
3. User-Agent устанавливается автоматически в `wikipedia_service.py`

### Ошибки при создании игры

Если получаете ошибку "Не удалось найти достижимую целевую статью":
- Wikipedia API может быть временно недоступен
- Попробуйте снова или укажите статьи вручную

### Ошибка 403 от Wikipedia

Убедитесь, что User-Agent установлен в `app/services/wikipedia_service.py` (уже настроен по умолчанию).

## Конфигурация Wikipedia API

Сервис использует следующие настройки:
- Rate limit: 10 запросов одновременно (настраивается в `.env`)
- Timeout: 10 секунд
- User-Agent: обязательно установлен для соответствия требованиям Wikipedia API

## Лицензия

MIT
