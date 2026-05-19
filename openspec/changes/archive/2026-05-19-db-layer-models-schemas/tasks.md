## 1. Dependencies & project structure

- [x] 1.1 Добавить в `apps/backend/requirements.txt` зависимости: `sqlalchemy[asyncio]>=2.0`, `asyncpg`, `alembic`, `pydantic-settings>=2.0`, `python-dotenv`
- [x] 1.2 Создать директорию `apps/backend/app/db/models/` с файлами `__init__.py`
- [x] 1.3 Создать директорию `apps/backend/app/schemas/` с файлом `__init__.py`

## 2. DB connection layer

- [x] 2.1 Создать `apps/backend/app/db/base.py` — объявить `Base = DeclarativeBase()`
- [x] 2.2 Создать `apps/backend/app/core/config.py` (если не существует) — добавить `Settings` с полем `DATABASE_URL: str` через `pydantic-settings BaseSettings`
- [x] 2.3 Создать `apps/backend/app/db/session.py` — создать `AsyncEngine` через `create_async_engine(settings.DATABASE_URL, echo=False)`, `AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)`, async-генератор `get_db()`
- [x] 2.4 Экспортировать `engine`, `AsyncSessionLocal`, `get_db`, `Base` из `apps/backend/app/db/__init__.py`

## 3. User model

- [x] 3.1 Создать `apps/backend/app/db/models/user.py` — объявить `class PlanEnum(str, enum.Enum)` со значениями `free`, `standart`, `pro`, `custom`
- [x] 3.2 Создать модель `User(Base)` с колонками: `id`, `keycloak_sub` (unique, index), `email`, `plan`, `cases_limit` (default 5), `subscription_ends_at`, `bonus_balance` (Numeric, default 0), `billing_updated_at`, `created_at`
- [x] 3.3 Убедиться, что `sa.Enum(PlanEnum, name="plan_enum")` передаётся в колонку `plan`

## 4. Case model

- [x] 4.1 Создать `apps/backend/app/db/models/case.py` — объявить `class CaseStatusEnum(str, enum.Enum)` со значениями `active`, `completed`, `archived`
- [x] 4.2 Создать модель `Case(Base)` с колонками: `id`, `user_id` (FK→users.id, CASCADE DELETE, index), `case_number` (nullable), `title`, `is_watched` (default False, index), `status` (default active), `source`, `yandex_disk_url`, `created_at`, `updated_at`
- [x] 4.3 Добавить relationship `user: Mapped[User] = relationship(back_populates="cases")` и обратный `cases` на модели `User`

## 5. Task model

- [x] 5.1 Создать `apps/backend/app/db/models/task.py` — модель `Task(Base)` с колонками: `id`, `user_id` (FK→users.id, CASCADE DELETE, index), `case_id` (FK→cases.id, SET NULL, nullable, index), `title` (not null), `description`, `is_done` (default False), `due_date`, `created_at`, `updated_at`
- [x] 5.2 Добавить relationship `user`, `case` и обратные `tasks` на `User` и `Case`

## 6. Note model

- [x] 6.1 Создать `apps/backend/app/db/models/note.py` — модель `Note(Base)` с колонками: `id`, `user_id` (FK→users.id, CASCADE DELETE, index), `case_id` (FK→cases.id, SET NULL, nullable, index), `title`, `content` (Text), `created_at`, `updated_at` (onupdate=func.now())
- [x] 6.2 Добавить relationship `user`, `case` и обратные `notes` на `User` и `Case`
- [x] 6.3 Экспортировать все модели из `apps/backend/app/db/models/__init__.py`

## 7. Pydantic schemas — User

- [x] 7.1 Создать `apps/backend/app/schemas/user.py` — `UserRead` с полями биллинга; `ConfigDict(from_attributes=True)`
- [x] 7.2 Добавить `BillingUpdate` схему для вебхука: `keycloak_sub`, `plan`, `cases_limit`, `subscription_ends_at`, `bonus_balance`

## 8. Pydantic schemas — Case, Task, Note

- [x] 8.1 Создать `apps/backend/app/schemas/case.py` — `CaseCreate`, `CaseRead`, `CaseUpdate`
- [x] 8.2 Создать `apps/backend/app/schemas/task.py` — `TaskCreate`, `TaskRead`, `TaskUpdate`
- [x] 8.3 Создать `apps/backend/app/schemas/note.py` — `NoteCreate`, `NoteRead`, `NoteUpdate`
- [x] 8.4 Экспортировать все схемы из `apps/backend/app/schemas/__init__.py`

## 9. Validation

- [x] 9.1 Убедиться, что `python -c "from app.db.models import User, Case, Task, Note"` выполняется без ошибок
- [x] 9.2 Убедиться, что `python -c "from app.schemas import UserRead, CaseRead, TaskRead, NoteRead"` выполняется без ошибок
- [x] 9.3 Проверить, что `Base.metadata.tables` содержит `users`, `cases`, `tasks`, `notes`
