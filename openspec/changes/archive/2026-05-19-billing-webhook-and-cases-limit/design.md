## Context

FastAPI-бэкенд имеет готовую модель `User` (поля `keycloak_sub`, `plan`, `cases_limit`, `subscription_ends_at`, `billing_updated_at`), модель `Case` (поле `is_watched`, FK `user_id`), async SQLAlchemy сессию и аутентификацию через Keycloak JWT (`get_current_user` из `app/api/deps.py`). Биллинговый сервис Юрайт.Суды инициирует вебхук при изменении подписки пользователя. Для ограничения бесплатного доступа необходим лимит-чек при создании дела.

## Goals / Non-Goals

**Goals:**
- Реализовать `POST /api/billing/update` с аутентификацией через статичный секрет (`BILLING_WEBHOOK_SECRET` в заголовке `X-Billing-Secret`).
- Обновлять поля `plan`, `cases_limit`, `subscription_ends_at`, `billing_updated_at` у пользователя, найденного по `keycloak_sub`.
- Считать текущее количество отслеживаемых дел пользователя (`is_watched = True`) через `COUNT` и сравнивать с `cases_limit` в сервисном слое.
- Возвращать `HTTP 402 Payment Required` при достижении лимита перед созданием нового дела.

**Non-Goals:**
- Реализация `POST /api/cases/save` (только добавление лимит-чека к будущему эндпоинту).
- Webhook signature verification (HMAC и т.п.) — используется простой статичный токен для MVP.
- Логирование истории изменений биллинга в отдельной таблице.
- Идемпотентность вебхука (повторные вызовы обновляют поля, что корректно).

## Decisions

### 1. Аутентификация вебхука: статичный токен в заголовке `X-Billing-Secret`

Биллинговый сервис передаёт секрет как HTTP-заголовок `X-Billing-Secret`. FastAPI-зависимость (`Depends`) сравнивает его с `settings.BILLING_WEBHOOK_SECRET` через `secrets.compare_digest` (защита от timing attacks). При несовпадении — `403 Forbidden`. Альтернатива HMAC-подпись тела — избыточна для MVP, когда вебхук от внутренней системы.

### 2. Поиск пользователя: по `keycloak_sub`

Вебхук содержит `keycloakSub` (строковый идентификатор). Используется `SELECT … WHERE keycloak_sub = :sub` с уже существующим уникальным индексом. Если пользователь не найден — `404 Not Found` (пользователь ещё не логинился; биллинг пришёл раньше первого входа). Это явная ошибка, не silent skip.

### 3. Подсчёт `casesUsed`: `COUNT(*) WHERE user_id = :id AND is_watched = True`

`casesUsed` не хранится в таблице `users` как денормализованное поле — это минимизирует риск рассинхронизации. Подсчёт через `SELECT COUNT(*)` с индексом по `(user_id, is_watched)` достаточно быстр для MVP-нагрузки. Альтернатива — поле `cases_used` в `users` с инкрементом/декрементом — создаёт риск расхождения при прямых SQL-операциях.

### 4. Структура: сервисный слой `app/services/billing.py`

Бизнес-логика (проверка лимита, обновление подписки) выделена в `app/services/billing.py`, роутер в `app/api/v1/billing.py`. Это согласуется с уже существующим паттерном проекта (deps → router → service). Лимит-чек вызывается из `app/api/v1/cases.py` как `await billing_service.check_cases_limit(db, user)`.

### 5. HTTP 402 для превышения лимита

Стандарт HTTP предусматривает `402 Payment Required` для ситуаций, требующих оплаты. FastAPI поднимает `HTTPException(status_code=402, detail="Cases limit reached")`. Фронтенд обрабатывает этот код для показа upgrade-банера.

## Risks / Trade-offs

- **COUNT при каждом создании дела** → лишний SQL-запрос перед INSERT. Для MVP (сотни дел на пользователя) незначим; при масштабировании — добавить `cases_used` в `users` с триггером или application-level инкрементом.
- **Статичный токен BILLING_WEBHOOK_SECRET** → при утечке токена — полный доступ к обновлению биллинга. Митигация: токен ротируется через переменную окружения без деплоя кода; в production перейти на HMAC.
- **404 при вебхуке до первого входа** → биллинговый сервис должен обрабатывать 404 и повторять запрос после логина пользователя. Альтернатива (upsert пользователя по вебхуку) требует email/данных, которых у биллинга может не быть.
- **Отсутствие идемпотентного ключа** → повторный вебхук просто перезаписывает поля теми же данными, что корректно.

## Migration Plan

1. Добавить `BILLING_WEBHOOK_SECRET` в `.env` и `core/config.py`.
2. Создать `app/services/billing.py` с функциями `update_subscription` и `check_cases_limit`.
3. Создать `app/api/v1/billing.py` с роутером и подключить в `main.py`.
4. В `app/api/v1/cases.py` добавить вызов `check_cases_limit` перед созданием дела.
5. Rollback: удалить `billing.py` роутер из `main.py`; остальные эндпоинты не затрагиваются.

## Open Questions

- Какой HTTP-заголовок использует биллинговый сервис: `X-Billing-Secret` или `Authorization`? → По умолчанию принято `X-Billing-Secret`; при уточнении — изменить только в `deps.py`.
- Нужно ли считать дела со статусом `archived` или только `active` в `casesUsed`? → Считаем только `is_watched = True` (независимо от статуса), т.к. это семантика "активного слежения".
