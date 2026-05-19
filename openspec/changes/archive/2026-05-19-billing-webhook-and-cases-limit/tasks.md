## 1. Конфигурация

- [x] 1.1 Добавить поле `BILLING_WEBHOOK_SECRET: str` в класс `Settings` в `apps/backend/core/config.py`
- [x] 1.2 Добавить `BILLING_WEBHOOK_SECRET` в `.env.example` (и реальный `.env`) с placeholder-значением

## 2. Сервисный слой

- [x] 2.1 Создать файл `apps/backend/app/services/__init__.py` (если не существует)
- [x] 2.2 Создать `apps/backend/app/services/billing.py` с функцией `update_subscription(db, data: BillingUpdateRequest) -> User`
- [x] 2.3 Добавить в `apps/backend/app/services/billing.py` функцию `check_cases_limit(db, user: User) -> None` с подсчётом `COUNT(*) WHERE user_id=user.id AND is_watched=True` и `HTTPException(402)` при `count >= user.cases_limit`

## 3. Pydantic-схема

- [x] 3.1 Добавить схему `BillingUpdateRequest` (поля: `keycloakSub: str`, `plan: str`, `casesLimit: int`, `subscriptionEndsAt: datetime | None`) в `apps/backend/app/schemas/billing.py` (создать файл)

## 4. Биллинговый роутер

- [x] 4.1 Создать `apps/backend/app/api/v1/billing.py` с FastAPI-роутером
- [x] 4.2 Реализовать зависимость `verify_billing_secret(x_billing_secret: str = Header(...))` в `apps/backend/app/api/deps.py`, сравнивающую через `secrets.compare_digest` и поднимающую `HTTP 403` при несовпадении
- [x] 4.3 Реализовать эндпоинт `POST /billing/update` в роутере: использовать `Depends(verify_billing_secret)`, вызвать `update_subscription`, вернуть `{"status": "ok"}`
- [x] 4.4 Смонтировать биллинговый роутер в `apps/backend/main.py` с префиксом `/api/billing`

## 5. Интеграция лимит-чека в cases

- [x] 5.1 В `apps/backend/app/api/v1/cases.py` (создать файл если не существует) в эндпоинте `POST /cases/save` добавить вызов `await check_cases_limit(db, current_user)` перед INSERT
- [x] 5.2 Убедиться, что при `HTTP 402` операция создания дела не выполняется (исключение прерывает обработку)

## 6. Проверка

- [ ] 6.1 Вручную проверить `POST /api/billing/update` с верным и неверным `X-Billing-Secret` через curl/Postman
- [ ] 6.2 Вручную проверить, что при достижении лимита `POST /api/cases/save` возвращает `HTTP 402`
- [ ] 6.3 Убедиться, что `GET /api/users/me` отражает обновлённые поля после вызова вебхука
