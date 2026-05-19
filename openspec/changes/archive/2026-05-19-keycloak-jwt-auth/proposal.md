## Why

Бэкенд FastAPI не имеет механизма аутентификации: все эндпоинты открыты, пользовательского контекста нет. Чтобы связать HTTP-запросы с конкретным пользователем и применять тарифные лимиты, необходима зависимость (Depends), которая проверяет Keycloak JWT и обеспечивает upsert пользователя в локальной БД.

## What Changes

- Новая зависимость `get_current_user` в `app/api/deps.py`, выполняющая валидацию Bearer JWT через JWKS Keycloak.
- Кэш JWKS с TTL для снижения нагрузки на Keycloak при каждом запросе.
- Upsert-логика: при первом входе создаёт запись `User` с тарифом `free` и лимитом `cases_limit=5`; при повторном — возвращает существующий объект из БД.
- Новый роутер `app/api/v1/users.py` с тестовым эндпоинтом `GET /api/users/me`, защищённым зависимостью.
- Подключение роутера в `main.py`.
- Добавление зависимостей `python-jose[cryptography]` и `httpx` в `requirements.txt`.

## Capabilities

### New Capabilities

- `keycloak-jwt-validation`: Валидация Bearer JWT-токенов через JWKS-эндпоинт Keycloak с кэшированием публичных ключей.
- `user-upsert`: Автоматическое создание/получение пользователя в PostgreSQL по `keycloak_sub` из JWT-токена.
- `users-me-endpoint`: Тестовый защищённый эндпоинт `GET /api/users/me`, возвращающий профиль текущего пользователя.

### Modified Capabilities

*(нет — существующие спецификации не затрагиваются)*

## Impact

- **Новые файлы:** `app/api/__init__.py`, `app/api/deps.py`, `app/api/v1/__init__.py`, `app/api/v1/users.py`
- **Изменённые файлы:** `main.py` (подключение роутера), `requirements.txt` (новые пакеты)
- **Зависимости:** `python-jose[cryptography]` (декодирование JWT), `httpx` (загрузка JWKS)
- **Переменные окружения:** используются существующие `KEYCLOAK_ISSUER` и `KEYCLOAK_CLIENT_ID` из `core/config.py`
- **БД:** только чтение/запись таблицы `users` через существующий `get_db` и модель `User`
