# WikiRush

WikiRush - это игра-гонка по Википедии, где игроки соревнуются в поиске кратчайшего пути между статьями, переходя по ссылкам внутри статей.

## Описание

WikiRush предлагает уникальный игровой опыт, основанный на структуре Википедии. Игроки начинают с одной статьи и должны найти путь к целевой статье, используя только ссылки внутри статей. Побеждает тот, кто найдет путь быстрее или за меньшее количество шагов.

### Основные возможности

- Случайная генерация начальной и целевой статей с гарантированным путём между ними
- Интеграция с русской Википедией
- Мультиплеер с real-time обновлениями через WebSocket
- Различные режимы игры (одиночный, мультиплеер)
- Просмотр доступных ссылок из текущей статьи
- Краткие описания статей для принятия решений
- Таблица лидеров
- Статистика игроков

## Технологии

### Backend
- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с поддержкой async/await
- **SQLite** - база данных для разработки (PostgreSQL для production)
- **Pydantic** - валидация данных и схемы
- **JWT** - аутентификация пользователей
- **WebSocket** - real-time обновления игр
- **httpx** - асинхронные HTTP запросы к Wikipedia API

### Frontend
- React / Vue.js (планируется)

## Структура проекта

```
WikiRush/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Конфигурация, БД, безопасность
│   │   ├── models/   # SQLAlchemy модели
│   │   ├── schemas/  # Pydantic схемы
│   │   └── services/ # Бизнес-логика
│   ├── tests/        # Тесты
│   └── README.md
├── frontend/         # Frontend приложение (планируется)
└── README.md
```

## Быстрый старт

### Требования

- Python 3.11+
- SQLite (для разработки) или PostgreSQL (для production)

### Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/wikirush.git
cd wikirush
```

2. Перейдите в директорию backend и создайте виртуальное окружение:
```bash
cd backend
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

4. Создайте файл `.env` на основе `.env.example`:
```bash
# Backend будет использовать SQLite по умолчанию
# Для production настройте PostgreSQL
```

5. Запустите сервер:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Откройте документацию API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Игровой процесс

1. **Регистрация/Вход** - создайте аккаунт или войдите
2. **Создание игры** - выберите режим и параметры игры (или используйте случайные статьи)
3. **Присоединение** - пригласите друзей или присоединитесь к существующей игре
4. **Старт** - создатель запускает игру
5. **Навигация** - переходите по ссылкам в статьях, пытаясь достичь цели
6. **Победа** - первый, кто достигнет целевой статьи, побеждает

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена

### Игры
- `POST /api/v1/games` - Создать игру
- `GET /api/v1/games` - Список игр
- `GET /api/v1/games/random-articles` - Получить случайные статьи с гарантированным путём
- `GET /api/v1/games/{id}` - Информация об игре
- `GET /api/v1/games/{id}/available-links` - Доступные ссылки из текущей позиции
- `POST /api/v1/games/{id}/join` - Присоединиться к игре
- `POST /api/v1/games/{id}/start` - Запустить игру
- `POST /api/v1/games/{id}/move` - Сделать ход
- `WS /api/v1/games/{id}/ws` - WebSocket для real-time обновлений

### Wikipedia
- `GET /api/v1/wikipedia/article/{title}/summary` - Краткое описание статьи
- `GET /api/v1/wikipedia/article/{title}/links` - Список ссылок из статьи
- `GET /api/v1/wikipedia/search` - Поиск статей

### Пользователи
- `GET /api/v1/users/me` - Текущий пользователь
- `GET /api/v1/users/{id}` - Информация о пользователе
- `GET /api/v1/users/{id}/stats` - Статистика пользователя

### Лидерборд
- `GET /api/v1/leaderboard` - Таблица лидеров

## Разработка

Подробная информация о разработке доступна в [backend/README.md](backend/README.md)

### Тестирование

```bash
cd backend
pytest
```

### Линтинг и форматирование

```bash
cd backend
# Форматирование
black .

# Линтинг
ruff check .

# Проверка типов
mypy app/
```

## Лицензия

MIT

## Контакты

Если у вас есть вопросы или предложения, создайте issue в репозитории.
