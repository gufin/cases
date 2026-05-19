## ADDED Requirements

### Requirement: Note table columns
`apps/backend/app/db/models/note.py` SHALL определять модель `Note` с таблицей `notes` и следующими колонками:

| Колонка | Тип SQLAlchemy | Ограничения |
|---|---|---|
| `id` | `Integer` | PK, autoincrement |
| `user_id` | `Integer` | FK → `users.id`, not null, index |
| `case_id` | `Integer` | FK → `cases.id`, nullable, index |
| `title` | `String(500)` | nullable |
| `content` | `Text` | nullable |
| `created_at` | `DateTime(timezone=True)` | not null, default `now()` |
| `updated_at` | `DateTime(timezone=True)` | nullable, onupdate `now()` |

#### Scenario: Заметка без привязки к делу
- **WHEN** создаётся `Note` с `user_id` но без `case_id`
- **THEN** запись сохраняется с `case_id = None`

### Requirement: Note-User foreign key with cascade
`notes.user_id` SHALL быть NOT NULL FK на `users.id` с DELETE CASCADE.

#### Scenario: Удаление пользователя удаляет его заметки
- **WHEN** из БД удаляется `User`
- **THEN** все связанные `Note` удаляются автоматически

### Requirement: Note-Case nullable foreign key
`notes.case_id` SHALL быть nullable FK на `cases.id` с SET NULL при удалении дела.

#### Scenario: Удаление дела обнуляет case_id в заметках
- **WHEN** удаляется `Case`
- **THEN** у связанных `Note` поле `case_id` становится `NULL`, заметки не удаляются

### Requirement: Auto-save friendly updated_at
`notes.updated_at` SHALL автоматически обновляться при каждом UPDATE через `onupdate=func.now()`.

#### Scenario: Редактор автосохранения обновляет updated_at
- **WHEN** обновляется `Note.content`
- **THEN** `updated_at` получает текущее время без явного указания в коде
