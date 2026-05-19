### Requirement: Сервисная функция check_cases_limit
`apps/backend/app/services/billing.py` SHALL содержать асинхронную функцию `check_cases_limit(db: AsyncSession, user: User) -> None`, которая:
1. Выполняет `SELECT COUNT(*) FROM cases WHERE user_id = user.id AND is_watched = True`.
2. Если `count >= user.cases_limit` — поднимает `HTTPException(status_code=402, detail="Cases limit reached. Please upgrade your plan.")`.
3. Если `count < user.cases_limit` — возвращает `None` без side-effects.

#### Scenario: Лимит не достигнут — функция возвращает без исключения
- **WHEN** у пользователя `cases_limit=5` и в БД 3 дела с `is_watched=True`
- **THEN** `check_cases_limit` завершается без `HTTPException`

#### Scenario: Лимит достигнут — функция поднимает HTTP 402
- **WHEN** у пользователя `cases_limit=5` и в БД 5 дел с `is_watched=True`
- **THEN** `check_cases_limit` поднимает `HTTPException(status_code=402)`

#### Scenario: Лимит превышен — функция поднимает HTTP 402
- **WHEN** у пользователя `cases_limit=5` и в БД 7 дел с `is_watched=True`
- **THEN** `check_cases_limit` поднимает `HTTPException(status_code=402)`

#### Scenario: Считаются только is_watched=True дела
- **WHEN** у пользователя 3 дела с `is_watched=True` и 10 дел с `is_watched=False`, `cases_limit=5`
- **THEN** `check_cases_limit` завершается без исключения (учитываются только 3 отслеживаемых)

### Requirement: Вызов check_cases_limit в POST /api/cases/save
Эндпоинт `POST /api/cases/save` SHALL вызывать `await check_cases_limit(db, current_user)` перед любой операцией INSERT в таблицу `cases`. Если `check_cases_limit` поднимает исключение, операция создания дела не выполняется.

#### Scenario: Создание дела при достигнутом лимите возвращает 402
- **WHEN** аутентифицированный пользователь с `cases_limit=5` и 5 активными делами вызывает `POST /api/cases/save`
- **THEN** сервер возвращает `HTTP 402 Payment Required` и дело не создаётся в БД

#### Scenario: Создание дела при свободном лимите продолжается нормально
- **WHEN** аутентифицированный пользователь с `cases_limit=5` и 2 активными делами вызывает `POST /api/cases/save` с корректными данными
- **THEN** сервер создаёт дело и возвращает `HTTP 200` или `HTTP 201`

### Requirement: HTTP 402 содержит понятное сообщение об ошибке
Ответ `HTTP 402` SHALL содержать JSON-тело `{"detail": "Cases limit reached. Please upgrade your plan."}`.

#### Scenario: Тело ответа 402 корректно сформировано
- **WHEN** сервер возвращает `HTTP 402` из-за превышения лимита
- **THEN** тело ответа: `{"detail": "Cases limit reached. Please upgrade your plan."}`
