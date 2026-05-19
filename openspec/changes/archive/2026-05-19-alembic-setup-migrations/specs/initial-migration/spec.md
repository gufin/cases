## ADDED Requirements

### Requirement: Миграция create_initial_tables создаёт все четыре таблицы
Файл ревизии в `apps/backend/migrations/versions/` с сообщением `create_initial_tables` SHALL содержать `upgrade()`, создающую таблицы `users`, `cases`, `tasks`, `notes` с правильными колонками и Foreign Key-ограничениями. `downgrade()` SHALL удалять эти таблицы в обратном порядке зависимостей.

#### Scenario: upgrade применяет схему к пустой БД
- **WHEN** выполняется `alembic upgrade head` против пустой PostgreSQL БД
- **THEN** в БД появляются таблицы `users`, `cases`, `tasks`, `notes`; `alembic_version` содержит head-ревизию

#### Scenario: downgrade откатывает схему
- **WHEN** выполняется `alembic downgrade base`
- **THEN** таблицы `users`, `cases`, `tasks`, `notes` удаляются из БД; `alembic_version` пуста

### Requirement: Колонки соответствуют SQLAlchemy-моделям
Таблицы в миграции SHALL содержать ровно те колонки, типы и ограничения, которые объявлены в моделях `app.db.models.*`. Расхождений между `autogenerate` и моделями MUST NOT быть.

#### Scenario: Повторный autogenerate не детектирует изменений
- **WHEN** миграция уже применена и выполняется `alembic revision --autogenerate -m "check"`
- **THEN** сгенерированный файл содержит пустые `upgrade()` и `downgrade()` (нет незамигрированных изменений)

### Requirement: down_revision равен None (начальная миграция)
Ревизионный файл SHALL иметь `down_revision = None`, подтверждая отсутствие истории миграций до него.

#### Scenario: Цепочка ревизий начинается с этого файла
- **WHEN** выполняется `alembic history`
- **THEN** в списке ровно одна ревизия с `down_revision = None`
