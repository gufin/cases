## Context

Бэкенд — FastAPI + SQLAlchemy (asyncio) + PostgreSQL через asyncpg. Модели (`User`, `Case`, `Task`, `Note`) и `Base` уже объявлены в `apps/backend/app/db/`. Конфиг читается через `pydantic-settings` из `core.config.settings`. Alembic присутствует в `requirements.txt`, но ещё не инициализирован. Сейчас таблицы не существуют в БД — приложение нельзя запустить.

## Goals / Non-Goals

**Goals:**
- Инициализировать Alembic с async-режимом (`asyncpg`).
- Связать `env.py` с `Base.metadata` и `settings.database_url` без дублирования URL.
- Автогенерировать первую миграцию, создающую все четыре таблицы.
- Обеспечить воспроизводимое применение схемы командой `alembic upgrade head`.

**Non-Goals:**
- Seed-данные и фикстуры.
- CI-автоматизация запуска миграций.
- Миграции в рамках отдельных модулей/микросервисов (multi-tenancy).

## Decisions

### Расположение: `apps/backend/migrations/` (не `alembic/`)

Alembic по умолчанию создаёт директорию `alembic/`. Используем `migrations/` — это соответствует соглашению FastAPI-проектов и явно отделяет папку от имени инструмента.

Альтернатива `alembic/` — отклонена: стандартное имя не несёт смысла; `migrations/` самодокументируется.

### Async env.py через `run_migrations_online` с `AsyncEngine`

Alembic по умолчанию использует синхронный `engine`. Для asyncpg необходим паттерн с `asyncio.run(run_async_migrations())` и `async_engine.connect()`. Синхронный fallback (`--autogenerate` offline) не нужен на данном этапе.

Альтернатива — синхронный psycopg2 только для миграций: отклонена, т.к. требует второй зависимости и расходится с runtime-конфигурацией.

### URL берётся из `settings.database_url`

`env.py` импортирует `from core.config import settings` — тот же источник истины, что и `session.py`. `alembic.ini` содержит placeholder `sqlalchemy.url = driver://...` — он игнорируется в runtime.

Альтернатива — переменная `ALEMBIC_DATABASE_URL` — отклонена: усложняет конфиг без выгоды.

### Первая миграция — автогенерация (`--autogenerate`)

Автогенерация сравнивает `Base.metadata` с пустой БД и строит `CREATE TABLE`. Ручная миграция избыточна при нулевой истории.

## Risks / Trade-offs

- **Импорт моделей в env.py** → Если хотя бы одна модель не импортирована до `target_metadata`, `autogenerate` «не видит» таблицу и не генерирует DDL.  
  Митигация: в `env.py` добавляем `import app.db.models` (или явные импорты каждой модели), чтобы все они зарегистрировались в `Base.metadata`.

- **`asyncpg` не поддерживает offline-миграции напрямую** → `alembic upgrade --sql` не работает с async-драйвером.  
  Митигация: документируем, что offline-режим не используется; при необходимости переключаемся на psycopg2 URL только для offline-генерации скриптов.

## Migration Plan

1. `alembic init migrations` — инициализация директории.
2. Правка `alembic.ini`: `script_location = migrations`.
3. Правка `migrations/env.py`: async-паттерн + `target_metadata = Base.metadata`.
4. `alembic revision --autogenerate -m "create_initial_tables"` — генерация файла миграции.
5. Ревью сгенерированного файла в `migrations/versions/`.
6. `alembic upgrade head` — применение к БД.

Rollback: `alembic downgrade base` удаляет все таблицы (миграция реализует `drop_table` в `downgrade()`).

## Open Questions

- Нужен ли `Enum`-тип PostgreSQL для полей `status`/`plan`? Если да — autogenerate создаст `sa.Enum(...)`, что правильно. Уточнить при ревью сгенерированного файла.
