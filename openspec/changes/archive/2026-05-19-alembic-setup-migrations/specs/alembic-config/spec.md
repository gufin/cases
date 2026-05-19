## ADDED Requirements

### Requirement: alembic.ini с корректным script_location
`apps/backend/alembic.ini` SHALL содержать `script_location = migrations`. Поле `sqlalchemy.url` SHALL присутствовать как placeholder и НЕ SHALL использоваться в runtime (URL подставляется в `env.py`).

#### Scenario: alembic.ini указывает на migrations/
- **WHEN** выполняется `alembic --config apps/backend/alembic.ini current`
- **THEN** Alembic находит директорию `apps/backend/migrations/` и не выдаёт ошибку пути

### Requirement: Async env.py с подключением через AsyncEngine
`apps/backend/migrations/env.py` SHALL реализовывать online-миграцию через `asyncio.run(run_async_migrations())`, используя `create_async_engine(settings.database_url)`. Синхронный `run_migrations_offline` SHALL присутствовать для совместимости, но МОЖЕТ бросать `NotImplementedError` при вызове с asyncpg URL.

#### Scenario: env.py импортирует settings и Base
- **WHEN** `migrations/env.py` загружается интерпретатором
- **THEN** `settings.database_url` успешно читается и `target_metadata` равен `Base.metadata` без ошибок импорта

#### Scenario: Все модели зарегистрированы в metadata
- **WHEN** в `env.py` выполняется `import app.db.models` (или явные импорты `User`, `Case`, `Task`, `Note`)
- **THEN** `Base.metadata.sorted_tables` содержит таблицы `users`, `cases`, `tasks`, `notes`

### Requirement: script.py.mako с корректным шаблоном ревизий
`apps/backend/migrations/script.py.mako` SHALL содержать стандартный шаблон Alembic с полями `revision`, `down_revision`, `branch_labels`, `depends_on`, функциями `upgrade()` и `downgrade()`.

#### Scenario: Новый файл ревизии генерируется из шаблона
- **WHEN** выполняется `alembic revision --autogenerate -m "test"`
- **THEN** в `migrations/versions/` создаётся `.py`-файл с корректным заголовком и функциями `upgrade`/`downgrade`
