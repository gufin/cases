## Context

Бэкенд FastAPI (`apps/backend/`) уже создан (bootstrap), но не имеет слоя БД. Предстоит построить фундамент: конфигурацию AsyncEngine для PostgreSQL, декларативные модели SQLAlchemy 2.0 (`User`, `Case`, `Task`, `Note`) и Pydantic v2-схемы для API-контрактов. Проект использует Python 3.11+, SQLAlchemy 2.0 в async-режиме, Alembic для миграций, Pydantic v2.

## Goals / Non-Goals

**Goals:**
- Async-совместимый `AsyncEngine` + `AsyncSession` с DI-функцией `get_db` для FastAPI.
- Декларативная `Base` (SQLAlchemy 2.0 `DeclarativeBase`) — единственная точка создания метаданных.
- Модели: `User`, `Case`, `Task`, `Note` со строго типизированными колонками и FK-связями.
- Pydantic v2-схемы (Create, Read, Update) для каждой сущности; схемы не наследуют ORM-модели напрямую, используется `model_config = ConfigDict(from_attributes=True)`.
- `plan` представлен Python `enum.Enum` и PostgreSQL `ENUM`-типом через `sqlalchemy.Enum`.

**Non-Goals:**
- Alembic-миграции не создаются в этом чейндже — это отдельная задача.
- Репозитории/сервисный слой не входят в скоуп.
- Роуты (эндпоинты) FastAPI не добавляются.
- Seeding / тестовые данные не входят в скоуп.

## Decisions

### 1. Async-режим SQLAlchemy 2.0

**Выбор:** `create_async_engine` + `async_sessionmaker` + `AsyncSession`.  
**Почему:** FastAPI нативно асинхронный; синхронный движок блокировал бы event loop. `asyncpg` — самый быстрый драйвер для PostgreSQL в Python.  
**Альтернатива:** `psycopg2` (sync) — отклонён, так как блокирует I/O.

### 2. Структура директорий

```
apps/backend/app/
├── db/
│   ├── __init__.py
│   ├── base.py          # DeclarativeBase
│   ├── session.py       # engine, AsyncSessionLocal, get_db
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── case.py
│       ├── task.py
│       └── note.py
└── schemas/
    ├── __init__.py
    ├── user.py
    ├── case.py
    ├── task.py
    └── note.py
```

**Почему:** Разделение `db/` и `schemas/` следует принципу единственной ответственности. ORM-модели ничего не знают о Pydantic, схемы ничего не знают о SQLAlchemy.

### 3. `plan` как Python Enum + SQLAlchemy Enum

**Выбор:** `class PlanEnum(str, enum.Enum)` + `sa.Enum(PlanEnum, name="plan_enum")`.  
**Почему:** Типобезопасность в Python и валидируемый тип в PostgreSQL. `str`-наследование позволяет напрямую использовать значения в Pydantic-схемах без доп. конвертации.

### 4. Поле `keycloak_sub` как `unique + not null`

**Выбор:** `String(255), unique=True, nullable=False, index=True`.  
**Почему:** Операция upsert `INSERT ... ON CONFLICT (keycloak_sub) DO UPDATE` требует уникального индекса. Значение берётся из поля `sub` JWT Keycloak и никогда не меняется.

### 5. UUID vs Integer PK

**Выбор:** `Integer` autoincrement (SERIAL) для всех таблиц на MVP.  
**Почему:** Проще в отладке, меньше нагрузки при JOIN; внешних API-клиентов, которым нужны непредсказуемые ID, нет. Можно мигрировать на UUID позже.

### 6. Nullable FK для `Case` в `Task` и `Note`

**Выбор:** `case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id"), nullable=True)`.  
**Почему:** ТЗ явно говорит, что задачи и заметки могут существовать без привязки к делу.

## Risks / Trade-offs

- **[Риск] Миграции не синхронизированы** → Без Alembic первый запуск потребует `Base.metadata.create_all`. Решение: следующий чейндж — Alembic setup.
- **[Риск] `plan_enum` PostgreSQL-тип сложно переименовать** → Mitigation: enum значения (`free`, `standart`, `pro`, `custom`) зафиксированы в ТЗ и не должны меняться.
- **[Trade-off] Integer PK vs UUID** → UUID даст лучшую распределённость, но Integer проще на MVP. Заменимо в будущем через Alembic.
- **[Риск] Circular imports `models/` → `schemas/`** → Решение: схемы импортируют из `models/` только `PlanEnum`; ORM-модели схемы не знают.
