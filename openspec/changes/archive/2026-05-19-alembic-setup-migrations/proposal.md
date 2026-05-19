## Why

Слой БД (модели SQLAlchemy, сессия) уже создан, но схема ни разу не применялась к реальной базе данных. Без Alembic невозможно воспроизводимо создать таблицы в PostgreSQL и управлять их эволюцией — запуск приложения или тестов сейчас упадёт с ошибкой «relation does not exist».

## What Changes

- Alembic инициализируется внутри `apps/backend/` с `async`-драйвером (`asyncpg`).
- `env.py` настраивается на `Base.metadata` из `app.db.base` и читает `DATABASE_URL` через `pydantic-settings` (тот же `settings.database_url`).
- Создаётся первая миграция `create_initial_tables`, которая автогенерирует DDL для таблиц `users`, `cases`, `tasks`, `notes`.
- `alembic.ini` хранит только шаблонный `sqlalchemy.url = driver://...`; реальный URL подставляется в `env.py` из `settings`.

## Capabilities

### New Capabilities

- `alembic-config`: Настройка Alembic для asyncpg — `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`.
- `initial-migration`: Первая авто-генерируемая миграция создающая таблицы `users`, `cases`, `tasks`, `notes`.

### Modified Capabilities

## Impact

- `apps/backend/alembic.ini` — новый файл конфигурации Alembic.
- `apps/backend/migrations/` — новая директория: `env.py`, `script.py.mako`, `versions/`.
- `apps/backend/requirements.txt` — `alembic` уже добавлен на предыдущем шаге; дополнительных зависимостей нет.
- Существующий код в `app/db/` не изменяется.
