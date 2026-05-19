## Why

Бэкенд CRM не имеет слоя базы данных: нет моделей SQLAlchemy, нет сессии и нет Pydantic-схем валидации. Без этого фундамента невозможно строить ни один API-эндпоинт — авторизацию, биллинг, дела, задачи и заметки.

## What Changes

- Добавляется конфигурация подключения к PostgreSQL (`engine`, async `sessionmaker`, `Base`) с чтением `DATABASE_URL` из окружения.
- Вводится модель `User` с полями биллинга (`plan` enum, `cases_limit`, `subscription_ends_at`, `bonus_balance`, `billing_updated_at`) и полем `keycloak_sub` для привязки к Keycloak JWT.
- Вводятся модели `Case`, `Task`, `Note` с внешними ключами на `User`.
- Добавляются базовые Pydantic v2-схемы (input/output) для каждой модели.
- Добавляется общий `Base` (DeclarativeBase) и базовая функция `get_db` для Dependency Injection в FastAPI.

## Capabilities

### New Capabilities

- `db-connection`: Конфигурация движка БД — `AsyncEngine`, `AsyncSessionLocal`, декларативный `Base`, `get_db` dependency.
- `user-model`: Модель `User` (таблица `users`) с биллинговыми полями и `keycloak_sub`.
- `case-model`: Модель `Case` (таблица `cases`) с полями `case_number`, `is_watched`, `status` и FK на `User`.
- `task-model`: Модель `Task` (таблица `tasks`) с FK на `User` и опциональным FK на `Case`.
- `note-model`: Модель `Note` (таблица `notes`) с FK на `User` и опциональным FK на `Case`.
- `pydantic-schemas`: Базовые Pydantic v2-схемы (Create / Read / Update) для `User`, `Case`, `Task`, `Note`.

### Modified Capabilities

## Impact

- `apps/backend/app/db/` — новая директория: `connection.py`, `base.py`, `models/`.
- `apps/backend/app/schemas/` — новая директория с Pydantic-схемами.
- `apps/backend/requirements.txt` — добавляются `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic-settings`.
- Никакие существующие публичные API не затрагиваются (эндпоинтов ещё нет).
