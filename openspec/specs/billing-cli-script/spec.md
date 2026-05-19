## ADDED Requirements

### Requirement: CLI-скрипт set_billing.py существует
`apps/backend/scripts/set_billing.py` SHALL существовать и запускаться командой:
```
docker compose exec backend python scripts/set_billing.py --email <email> --plan <plan> --limit <int> --days <int>
```

#### Scenario: Скрипт доступен внутри контейнера
- **WHEN** выполняется `docker compose exec backend python scripts/set_billing.py --help`
- **THEN** скрипт выводит справку с описанием аргументов и завершается с кодом 0

### Requirement: Поиск пользователя по email
Скрипт SHALL искать пользователя в таблице `users` по полю `email`. Если пользователь не найден — выводить сообщение об ошибке и завершаться с кодом 1.

#### Scenario: Пользователь найден
- **WHEN** передан `--email user@example.com` и пользователь с таким email существует в БД
- **THEN** скрипт обновляет его биллинговые поля

#### Scenario: Пользователь не найден
- **WHEN** передан `--email unknown@example.com` и такого пользователя нет в БД
- **THEN** скрипт выводит `Пользователь с email 'unknown@example.com' не найден.` и завершается с кодом 1

### Requirement: Обновление биллинговых полей
Скрипт SHALL обновлять следующие поля модели `User`:

| Аргумент CLI | Поле в БД | Описание |
|---|---|---|
| `--plan` | `plan` | Значение из `PlanEnum` (`free`, `standart`, `pro`, `custom`) |
| `--limit` | `cases_limit` | Целое число — максимум дел |
| `--days` | `subscription_ends_at` | `now() + timedelta(days=N)`; если `0` — устанавливается `null` |

После обновления SHALL устанавливать `billing_updated_at = now()`.

#### Scenario: Успешное обновление плана и лимита
- **WHEN** передано `--email user@example.com --plan pro --limit 100 --days 30`
- **THEN** у пользователя устанавливается `plan=pro`, `cases_limit=100`, `subscription_ends_at=now()+30d`, `billing_updated_at=now()`
- **THEN** скрипт выводит итоговые значения полей и завершается с кодом 0

#### Scenario: Обнуление подписки через --days 0
- **WHEN** передано `--days 0`
- **THEN** поле `subscription_ends_at` устанавливается в `null` (бессрочная подписка)

### Requirement: Валидация значения --plan
Скрипт SHALL принимать только допустимые значения `PlanEnum`: `free`, `standart`, `pro`, `custom`. При недопустимом значении — выводить ошибку и завершаться с кодом 2.

#### Scenario: Недопустимый план
- **WHEN** передано `--plan enterprise`
- **THEN** скрипт выводит `Недопустимый план 'enterprise'. Допустимые значения: free, standart, pro, custom.` и завершается с кодом 2

### Requirement: Все аргументы опциональны
Скрипт SHALL обновлять только те поля, для которых аргументы были явно переданы. Непереданные аргументы SHALL оставлять соответствующие поля в БД без изменений.

#### Scenario: Обновление только лимита без изменения плана
- **WHEN** передано `--email user@example.com --limit 50`
- **THEN** обновляется только `cases_limit=50`; поля `plan`, `subscription_ends_at` остаются прежними
