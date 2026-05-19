## 1. Инициализация Alembic

- [x] 1.1 Запустить `alembic init migrations` из директории `apps/backend/`
- [x] 1.2 Обновить `alembic.ini`: установить `script_location = migrations`, оставить `sqlalchemy.url` как placeholder

## 2. Настройка env.py

- [x] 2.1 Заменить содержимое `migrations/env.py` на async-паттерн с `asyncio.run(run_async_migrations())`
- [x] 2.2 Добавить импорт `from core.config import settings` и установить `config.set_main_option("sqlalchemy.url", settings.database_url)`
- [x] 2.3 Добавить импорты всех моделей (`from app.db.base import Base` + `import app.db.models`) и установить `target_metadata = Base.metadata`
- [x] 2.4 Реализовать `run_async_migrations()` с `async_engine.connect()` и `connection.run_sync(do_run_migrations)`

## 3. Генерация первой миграции

- [x] 3.1 Убедиться, что PostgreSQL запущен и `DATABASE_URL` задан в `.env`
- [x] 3.2 Выполнить `alembic revision --autogenerate -m "create_initial_tables"`
- [x] 3.3 Проверить сгенерированный файл в `migrations/versions/`: наличие четырёх `op.create_table(...)` и корректных `op.drop_table(...)` в `downgrade()`
- [x] 3.4 Убедиться, что `down_revision = None`

## 4. Применение и проверка

- [x] 4.1 Выполнить `alembic upgrade head` и убедиться в отсутствии ошибок
- [x] 4.2 Проверить через `psql` или `alembic current`, что таблицы `users`, `cases`, `tasks`, `notes` созданы
- [x] 4.3 Выполнить повторный `alembic revision --autogenerate -m "check"` и убедиться, что `upgrade()`/`downgrade()` пусты (нет расхождений)
- [x] 4.4 Выполнить `alembic downgrade base` и убедиться, что таблицы удалены; затем снова `alembic upgrade head`
