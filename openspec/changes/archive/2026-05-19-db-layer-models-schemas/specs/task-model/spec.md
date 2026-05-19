## ADDED Requirements

### Requirement: Task table columns
`apps/backend/app/db/models/task.py` SHALL определять модель `Task` с таблицей `tasks` и следующими колонками:

| Колонка | Тип SQLAlchemy | Ограничения |
|---|---|---|
| `id` | `Integer` | PK, autoincrement |
| `user_id` | `Integer` | FK → `users.id`, not null, index |
| `case_id` | `Integer` | FK → `cases.id`, nullable, index |
| `title` | `String(500)` | not null |
| `description` | `Text` | nullable |
| `is_done` | `Boolean` | not null, default `False` |
| `due_date` | `DateTime(timezone=True)` | nullable |
| `created_at` | `DateTime(timezone=True)` | not null, default `now()` |
| `updated_at` | `DateTime(timezone=True)` | nullable, onupdate `now()` |

#### Scenario: Задача без привязки к делу
- **WHEN** создаётся `Task` с `user_id` но без `case_id`
- **THEN** запись сохраняется с `case_id = None`

### Requirement: Task-User foreign key with cascade
`tasks.user_id` SHALL быть NOT NULL FK на `users.id` с DELETE CASCADE.

#### Scenario: Удаление пользователя удаляет его задачи
- **WHEN** из БД удаляется `User`
- **THEN** все связанные `Task` удаляются автоматически

### Requirement: Task-Case nullable foreign key
`tasks.case_id` SHALL быть nullable FK на `cases.id` с SET NULL при удалении дела.

#### Scenario: Удаление дела обнуляет case_id в задачах
- **WHEN** удаляется `Case`
- **THEN** у связанных `Task` поле `case_id` становится `NULL`, задачи не удаляются
