## 1. Зависимости и конфигурация

- [x] 1.1 Добавить `python-jose[cryptography]` и `httpx` в `apps/backend/requirements.txt`
- [x] 1.2 Добавить поле `keycloak_verify_aud: bool = False` в `core/config.py` (Settings)

## 2. JWKS-кэш и валидация JWT

- [x] 2.1 Создать `apps/backend/app/api/__init__.py` (пустой)
- [x] 2.2 Создать `apps/backend/app/api/deps.py` с модульным кэшем JWKS (`_jwks_cache: dict`, `_jwks_fetched_at: datetime | None`, TTL 5 минут)
- [x] 2.3 Реализовать async-функцию `_get_jwks()` в `deps.py`: проверяет TTL, при необходимости делает `httpx.AsyncClient().get(f"{settings.keycloak_issuer}/protocol/openid-connect/certs")`, кэширует результат, при ошибке поднимает `HTTPException(401)`
- [x] 2.4 Реализовать async-функцию `get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db))` в `deps.py`:
  - Парсит `Bearer <token>` из заголовка; при отсутствии → `401`
  - Вызывает `_get_jwks()`, декодирует токен через `jose.jwt.decode` (RS256, issuer=`settings.keycloak_issuer`)
  - Извлекает `sub`; при отсутствии → `401`
  - Вызывает `upsert_user(db, sub)` и возвращает `User`

## 3. Upsert пользователя

- [x] 3.1 Реализовать async-функцию `upsert_user(db: AsyncSession, keycloak_sub: str) -> User` в `deps.py` (или отдельном `app/services/user_service.py`):
  - `INSERT INTO users (keycloak_sub, plan, cases_limit) VALUES (...) ON CONFLICT (keycloak_sub) DO NOTHING`
  - `SELECT * FROM users WHERE keycloak_sub = ?`
  - Возвращает объект `User`

## 4. Роутер users и эндпоинт /me

- [x] 4.1 Создать `apps/backend/app/api/v1/__init__.py` (пустой)
- [x] 4.2 Создать `apps/backend/app/api/v1/users.py` с `APIRouter(prefix="/users", tags=["users"])`
- [x] 4.3 Добавить `GET /me` хэндлер, защищённый `Depends(get_current_user)`, возвращающий `UserRead.model_validate(user)`

## 5. Подключение роутера в main.py

- [x] 5.1 Импортировать `users` роутер в `main.py` и подключить через `app.include_router(users_router, prefix="/api")`
- [x] 5.2 Убедиться, что `GET /api/health` по-прежнему работает (нет конфликтов prefix)

## 6. Ручная проверка

- [ ] 6.1 Запустить `docker compose up` (или uvicorn локально), получить токен из Keycloak и выполнить `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/me` — убедиться в HTTP 200 с полями пользователя
- [ ] 6.2 Выполнить тот же запрос без токена — убедиться в HTTP 401
- [ ] 6.3 Проверить в БД, что запись в `users` создана с `plan=free`, `cases_limit=5`

