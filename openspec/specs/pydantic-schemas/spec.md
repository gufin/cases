## ADDED Requirements

### Requirement: Pydantic v2 schema configuration
Все Pydantic-схемы SHALL использовать `model_config = ConfigDict(from_attributes=True)` для поддержки `model_validate(orm_instance)`.

#### Scenario: Схема создаётся из ORM-объекта
- **WHEN** вызывается `UserRead.model_validate(user_orm_instance)`
- **THEN** возвращается корректно заполненный Pydantic-объект без ошибок

### Requirement: UserRead schema
`apps/backend/app/schemas/user.py` SHALL определять `UserRead` с полями: `id`, `keycloak_sub`, `email`, `plan`, `cases_limit`, `subscription_ends_at`, `bonus_balance`, `billing_updated_at`, `created_at`.

#### Scenario: UserRead сериализуется в JSON
- **WHEN** `UserRead.model_validate(user)` вызывается на ORM-объекте
- **THEN** поле `plan` сериализуется как строка (значение enum), `bonus_balance` как число

### Requirement: BillingUpdate schema
`apps/backend/app/schemas/user.py` SHALL определять `BillingUpdate` с полями: `keycloak_sub: str`, `plan: PlanEnum`, `cases_limit: int`, `subscription_ends_at: datetime | None`, `bonus_balance: Decimal`.

Эта схема используется для вебхука `POST /api/billing/update`.

#### Scenario: BillingUpdate валидирует план
- **WHEN** передаётся `plan = "invalid_plan"`
- **THEN** Pydantic возвращает `ValidationError`

### Requirement: CaseCreate and CaseRead schemas
`apps/backend/app/schemas/case.py` SHALL определять:
- `CaseCreate`: `case_number: str | None`, `title: str | None`, `source: str | None`, `yandex_disk_url: str | None`
- `CaseRead`: все поля `CaseCreate` + `id`, `user_id`, `is_watched`, `status`, `created_at`, `updated_at`
- `CaseUpdate`: `title: str | None`, `is_watched: bool | None`, `status: CaseStatusEnum | None`, `yandex_disk_url: str | None`

#### Scenario: CaseRead содержит is_watched
- **WHEN** `CaseRead.model_validate(case_orm)` вызывается
- **THEN** поле `is_watched` корректно отражает значение из БД

### Requirement: TaskCreate and TaskRead schemas
`apps/backend/app/schemas/task.py` SHALL определять:
- `TaskCreate`: `title: str`, `description: str | None`, `case_id: int | None`, `due_date: datetime | None`
- `TaskRead`: все поля `TaskCreate` + `id`, `user_id`, `is_done`, `created_at`, `updated_at`
- `TaskUpdate`: `title: str | None`, `description: str | None`, `is_done: bool | None`, `due_date: datetime | None`

#### Scenario: TaskCreate валидирует обязательный title
- **WHEN** `TaskCreate` создаётся без `title`
- **THEN** Pydantic возвращает `ValidationError`

### Requirement: NoteCreate and NoteRead schemas
`apps/backend/app/schemas/note.py` SHALL определять:
- `NoteCreate`: `title: str | None`, `content: str | None`, `case_id: int | None`
- `NoteRead`: все поля `NoteCreate` + `id`, `user_id`, `created_at`, `updated_at`
- `NoteUpdate`: `title: str | None`, `content: str | None`

#### Scenario: NoteRead содержит updated_at
- **WHEN** `NoteRead.model_validate(note_orm)` вызывается после обновления заметки
- **THEN** `updated_at` содержит актуальное время изменения
