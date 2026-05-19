## ADDED Requirements

### Requirement: User table columns
`apps/backend/app/db/models/user.py` SHALL определять модель `User` с таблицей `users` и следующими колонками:

| Колонка | Тип SQLAlchemy | Ограничения |
|---|---|---|
| `id` | `Integer` | PK, autoincrement |
| `keycloak_sub` | `String(255)` | unique, not null, index |
| `email` | `String(255)` | nullable |
| `plan` | `Enum(PlanEnum)` | not null, default `free` |
| `cases_limit` | `Integer` | not null, default `5` |
| `subscription_ends_at` | `DateTime(timezone=True)` | nullable |
| `bonus_balance` | `Numeric(12,2)` | not null, default `0` |
| `billing_updated_at` | `DateTime(timezone=True)` | nullable |
| `created_at` | `DateTime(timezone=True)` | not null, default `now()` |

#### Scenario: Пользователь создаётся с дефолтными биллинговыми значениями
- **WHEN** создаётся новый `User` с указанием только `keycloak_sub`
- **THEN** поле `plan` равно `PlanEnum.free`, `cases_limit` равно `5`, `bonus_balance` равно `0`

### Requirement: PlanEnum definition
`apps/backend/app/db/models/user.py` SHALL определять `class PlanEnum(str, enum.Enum)` со значениями `free`, `standart`, `pro`, `custom`.

#### Scenario: PlanEnum значения совпадают с ТЗ
- **WHEN** происходит сравнение `PlanEnum.free.value`
- **THEN** возвращается строка `"free"`

### Requirement: keycloak_sub уникален
`users.keycloak_sub` SHALL иметь уникальный индекс, обеспечивающий upsert-операцию `INSERT ... ON CONFLICT (keycloak_sub) DO UPDATE`.

#### Scenario: Повторная вставка с тем же keycloak_sub вызывает конфликт
- **WHEN** выполняется INSERT с уже существующим `keycloak_sub`
- **THEN** база данных возвращает `UniqueViolation`, что позволяет реализовать upsert логику
