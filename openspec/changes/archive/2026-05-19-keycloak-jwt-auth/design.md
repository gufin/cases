## Context

FastAPI-бэкенд имеет готовую модель `User` (поля `keycloak_sub`, `plan`, `cases_limit`), async SQLAlchemy сессию (`get_db`) и `core/config.py` с `keycloak_issuer`/`keycloak_client_id`. Никакой аутентификации нет. Keycloak (id.you-right.ru, realm You-right) выдаёт токены формата RS256 JWT; публичные ключи публикуются через стандартный JWKS-эндпоинт (`{issuer}/protocol/openid-connect/certs`).

## Goals / Non-Goals

**Goals:**
- Реализовать `get_current_user` как FastAPI Depends без side-effect при каждом запросе кроме DB-upsert.
- Валидировать подпись RS256, `exp`, `iss`, `aud` (client_id).
- Кэшировать JWKS в памяти процесса с TTL 5 минут, чтобы избежать round-trip к Keycloak на каждый запрос.
- Выполнять SELECT + INSERT (upsert) атомарно через `ON CONFLICT DO NOTHING` или эквивалент, возвращая актуальный объект `User`.
- Отдавать `401 Unauthorized` при невалидном токене, `403 Forbidden` если токен валиден но пользователь деактивирован (расширение в будущем).

**Non-Goals:**
- Refresh-токены, logout, session management (это зона NextAuth на фронте).
- Role-based access control — только идентификация пользователя.
- Rate limiting или throttling JWKS-запросов сверх простого TTL-кэша.
- Интеграционные тесты с реальным Keycloak в рамках этого изменения.

## Decisions

### 1. Библиотека для JWT: `python-jose[cryptography]`

`python-jose` поддерживает RS256 и умеет получать ключ прямо из JWKS-словаря (`jose.jwt.decode`). Альтернатива `PyJWT` требует вручную выбирать ключ по `kid`. `authlib` — избыточна для серверной валидации без клиентских потоков.

### 2. Загрузка JWKS: `httpx` (async)

Весь FastAPI-стек асинхронный (asyncpg, async SQLAlchemy). Использование синхронного `requests` заблокировало бы event loop. `httpx.AsyncClient` органично вписывается. JWKS кэшируется в module-level переменной `dict + timestamp`; на 5 минут хватает для production-нагрузки MVP.

### 3. Upsert: `INSERT … ON CONFLICT (keycloak_sub) DO NOTHING` + повторный SELECT

SQLAlchemy 2.0 поддерживает `insert().on_conflict_do_nothing()` (PostgreSQL диалект). Это race-condition safe: параллельные запросы от одного пользователя не создадут дублей. После INSERT всегда делается SELECT для получения полного объекта (включая server-generated `id`, `created_at`).

### 4. Структура директорий: `app/api/deps.py` + `app/api/v1/users.py`

Соответствует стандартному layout FastAPI-проектов и оставляет место для будущих `v1/cases.py`, `v1/tasks.py` и т.д. Роутер монтируется в `main.py` с префиксом `/api`.

### 5. Ответ `GET /api/users/me`: существующая схема `UserRead`

Схема уже определена в `app/schemas/user.py` и включает `id`, `email`, `plan`, `cases_limit`, `subscription_ends_at`. Не нужно создавать новую.

## Risks / Trade-offs

- **In-memory JWKS кэш не синхронизирован между воркерами** → при развёртывании с несколькими uvicorn-воркерами каждый будет делать свой запрос к Keycloak. Для MVP (1 воркер) приемлемо; при масштабировании — перенести в Redis.
- **`python-jose` не получала обновлений с 2022** → при обнаружении CVE заменить на `joserfc` (drop-in по API). Для MVP риск низкий.
- **TTL 5 минут на JWKS**: при ротации ключей в Keycloak может быть окно в 5 минут с невалидными проверками → приемлемо для MVP, в production снизить до 1 минуты или реализовать `kid`-based инвалидацию.
- **`ON CONFLICT DO NOTHING`**: если в будущем понадобится обновлять поля при логине (например `last_login_at`) — потребуется замена на `ON CONFLICT DO UPDATE`.

## Migration Plan

1. Добавить `python-jose[cryptography]` и `httpx` в `requirements.txt` и пересобрать образ.
2. Задеплоить новые файлы; новый роутер монтируется, существующий `GET /api/health` не затрагивается.
3. Убедиться, что `.env` содержит корректные `KEYCLOAK_ISSUER` и `KEYCLOAK_CLIENT_ID`.
4. Проверить `GET /api/users/me` с реальным токеном из Keycloak (`Authorization: Bearer <token>`).
5. Rollback: откат коммита; роутер исчезает, остальные эндпоинты не затронуты.

## Open Questions

- Нужно ли валидировать `aud` claim? Keycloak по умолчанию может не включать `client_id` в `aud` если не настроен mapper. Решение: попытаться валидировать, при ошибке — логировать warning и пропускать (конфигурируемый флаг `KEYCLOAK_VERIFY_AUD` в settings).
