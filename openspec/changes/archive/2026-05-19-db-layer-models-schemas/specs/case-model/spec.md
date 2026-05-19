## ADDED Requirements

### Requirement: Case table columns
`apps/backend/app/db/models/case.py` SHALL определять модель `Case` с таблицей `cases` и следующими колонками:

| Колонка | Тип SQLAlchemy | Ограничения |
|---|---|---|
| `id` | `Integer` | PK, autoincrement |
| `user_id` | `Integer` | FK → `users.id`, not null, index |
| `case_number` | `String(100)` | nullable (дела без номера разрешены) |
| `title` | `String(500)` | nullable |
| `is_watched` | `Boolean` | not null, default `False` |
| `status` | `Enum(CaseStatusEnum)` | not null, default `active` |
| `source` | `String(50)` | nullable (kad / gas) |
| `yandex_disk_url` | `String(2000)` | nullable |
| `created_at` | `DateTime(timezone=True)` | not null, default `now()` |
| `updated_at` | `DateTime(timezone=True)` | nullable, onupdate `now()` |

#### Scenario: Дело создаётся без номера
- **WHEN** создаётся `Case` с `user_id` но без `case_number`
- **THEN** запись сохраняется с `case_number = None` и `is_watched = False`

### Requirement: CaseStatusEnum definition
`apps/backend/app/db/models/case.py` SHALL определять `class CaseStatusEnum(str, enum.Enum)` со значениями `active`, `completed`, `archived`.

#### Scenario: CaseStatusEnum значения существуют
- **WHEN** проверяются члены `CaseStatusEnum`
- **THEN** доступны `active`, `completed`, `archived`

### Requirement: Case-User foreign key
`cases.user_id` SHALL быть NOT NULL FK на `users.id` с каскадным удалением (DELETE CASCADE).

#### Scenario: Удаление пользователя удаляет его дела
- **WHEN** из БД удаляется `User`
- **THEN** все связанные `Case` удаляются автоматически через CASCADE

### Requirement: is_watched index
Колонка `cases.is_watched` SHALL быть проиндексирована для быстрого выбора отслеживаемых дел в фоновом синхронизаторе.

#### Scenario: Запрос is_watched=True работает эффективно
- **WHEN** фоновый воркер выполняет `SELECT * FROM cases WHERE is_watched = true`
- **THEN** запрос использует индекс и не делает full table scan
