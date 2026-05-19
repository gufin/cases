## ADDED Requirements

### Requirement: Async database engine configuration
`apps/backend/app/db/session.py` SHALL export `AsyncEngine` создаваемый через `create_async_engine(DATABASE_URL)`, где `DATABASE_URL` читается из переменной окружения через `pydantic-settings`.

#### Scenario: Engine создаётся из переменной окружения
- **WHEN** переменная `DATABASE_URL` задана в `.env` в формате `postgresql+asyncpg://...`
- **THEN** `create_async_engine` принимает это значение и создаёт рабочий движок без ошибок

### Requirement: Async session factory
`apps/backend/app/db/session.py` SHALL экспортировать `AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)`.

#### Scenario: Сессия создаётся корректно
- **WHEN** вызывается `async with AsyncSessionLocal() as session`
- **THEN** возвращается экземпляр `AsyncSession` без ошибок

### Requirement: FastAPI dependency get_db
`apps/backend/app/db/session.py` SHALL предоставлять async-генератор `get_db()` возвращающий `AsyncSession` и закрывающий её после завершения запроса.

#### Scenario: Dependency injection работает в роуте
- **WHEN** роут FastAPI объявляет `db: AsyncSession = Depends(get_db)`
- **THEN** `db` является рабочей `AsyncSession` и автоматически закрывается после ответа

### Requirement: Единственный DeclarativeBase
`apps/backend/app/db/base.py` SHALL объявлять ровно один `Base = DeclarativeBase()`. Все модели MUST наследоваться от этого `Base`.

#### Scenario: Base импортируется и используется моделями
- **WHEN** модели `User`, `Case`, `Task`, `Note` импортируют `Base` из `app.db.base`
- **THEN** все таблицы регистрируются в `Base.metadata`
