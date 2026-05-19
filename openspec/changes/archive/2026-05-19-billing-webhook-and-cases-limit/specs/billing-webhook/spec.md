## ADDED Requirements

### Requirement: POST /api/billing/update endpoint
`apps/backend/app/api/v1/billing.py` SHALL определять роутер с эндпоинтом `POST /api/billing/update`, смонтированным в `main.py` с префиксом `/api`.

#### Scenario: Роутер зарегистрирован в приложении
- **WHEN** приложение FastAPI запускается
- **THEN** маршрут `POST /api/billing/update` присутствует в `app.routes`

### Requirement: Аутентификация через заголовок X-Billing-Secret
Эндпоинт `POST /api/billing/update` SHALL требовать заголовок `X-Billing-Secret`, значение которого сравнивается с `settings.BILLING_WEBHOOK_SECRET` через `secrets.compare_digest`. При несовпадении SHALL возвращать `HTTP 403 Forbidden`.

#### Scenario: Верный секрет — запрос проходит
- **WHEN** клиент отправляет `POST /api/billing/update` с корректным `X-Billing-Secret`
- **THEN** сервер обрабатывает запрос и возвращает `HTTP 200`

#### Scenario: Неверный секрет — запрос отклоняется
- **WHEN** клиент отправляет `POST /api/billing/update` с неверным `X-Billing-Secret`
- **THEN** сервер возвращает `HTTP 403 Forbidden`

#### Scenario: Отсутствующий заголовок — запрос отклоняется
- **WHEN** клиент отправляет `POST /api/billing/update` без заголовка `X-Billing-Secret`
- **THEN** сервер возвращает `HTTP 422 Unprocessable Entity` или `HTTP 403 Forbidden`

### Requirement: Тело запроса BillingUpdateRequest
Эндпоинт SHALL принимать JSON-тело со следующими полями (Pydantic v2 схема `BillingUpdateRequest`):

| Поле | Тип | Обязательность |
|---|---|---|
| `keycloakSub` | `str` | обязательное |
| `plan` | `str` | обязательное |
| `casesLimit` | `int` | обязательное |
| `subscriptionEndsAt` | `datetime \| None` | опциональное, `None` если нет подписки |

#### Scenario: Корректное тело разбирается без ошибок
- **WHEN** тело содержит все обязательные поля с корректными типами
- **THEN** Pydantic не выбрасывает `ValidationError`

#### Scenario: Отсутствие обязательного поля
- **WHEN** в теле отсутствует поле `keycloakSub`
- **THEN** сервер возвращает `HTTP 422 Unprocessable Entity`

### Requirement: Обновление полей подписки пользователя
Сервисная функция `update_subscription(db, data: BillingUpdateRequest)` в `apps/backend/app/services/billing.py` SHALL:
1. Найти пользователя по `keycloak_sub = data.keycloakSub`.
2. Если пользователь не найден — поднять `HTTPException(status_code=404)`.
3. Обновить поля `plan`, `cases_limit`, `subscription_ends_at`, `billing_updated_at = datetime.now(UTC)`.
4. Выполнить `await db.commit()`.
5. Вернуть обновлённый объект `User`.

#### Scenario: Успешное обновление подписки
- **WHEN** вебхук содержит `keycloakSub` существующего пользователя, `plan="pro"`, `casesLimit=50`, `subscriptionEndsAt="2027-01-01T00:00:00Z"`
- **THEN** поля `user.plan`, `user.cases_limit`, `user.subscription_ends_at` обновляются в БД, `user.billing_updated_at` устанавливается в текущее UTC-время

#### Scenario: Пользователь не найден
- **WHEN** вебхук содержит `keycloakSub`, которого нет в таблице `users`
- **THEN** сервер возвращает `HTTP 404 Not Found`

#### Scenario: Обновление с subscriptionEndsAt=null
- **WHEN** вебхук содержит `subscriptionEndsAt=null`
- **THEN** поле `user.subscription_ends_at` устанавливается в `None`

### Requirement: BILLING_WEBHOOK_SECRET в настройках
`apps/backend/core/config.py` SHALL содержать поле `BILLING_WEBHOOK_SECRET: str` в классе `Settings` (Pydantic v2 `BaseSettings`). Значение читается из переменной окружения `BILLING_WEBHOOK_SECRET`.

#### Scenario: Переменная окружения применяется
- **WHEN** переменная окружения `BILLING_WEBHOOK_SECRET` установлена в `"test-secret"`
- **THEN** `settings.BILLING_WEBHOOK_SECRET == "test-secret"`
