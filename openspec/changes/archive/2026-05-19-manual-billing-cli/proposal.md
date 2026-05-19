## Why

Платёжный хаб Юрайт ещё не запущен, поэтому нет автоматического способа изменить тарифный план пользователя. Администратору нужен инструмент для ручного управления лимитами прямо из терминала без прямого SQL.

## What Changes

- Добавляется CLI-скрипт `scripts/set_billing.py` внутри контейнера `backend`
- Скрипт принимает параметры: `--email`, `--plan`, `--limit`, `--days`
- Обновляет поля `plan`, `cases_limit`, `subscription_ends_at`, `billing_updated_at` в таблице `users`
- Запускается через `docker compose exec backend python scripts/set_billing.py ...`

## Capabilities

### New Capabilities

- `billing-cli-script`: CLI-скрипт для ручного управления тарифом и лимитами пользователя в обход платёжного хаба

### Modified Capabilities

## Impact

- Новый файл `backend/scripts/set_billing.py`
- Читает `DATABASE_URL` из переменных окружения
- Использует существующую SQLAlchemy-модель `User` и сессию БД
- Не затрагивает API-слой и не добавляет новых эндпоинтов
