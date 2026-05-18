## 1. Структура монорепозитория

- [x] 1.1 Создать директории `apps/backend`, `apps/frontend`, `docker` в корне репозитория
- [x] 1.2 Создать `.gitignore` с исключениями для `__pycache__`, `*.pyc`, `.env`, `node_modules`, `.next`, `*.egg-info`
- [x] 1.3 Создать `.env.example` с шаблоном всех переменных окружения из ТЗ (DATABASE_URL, ENV, SECRET_KEY, KEYCLOAK_*, NEXTAUTH_*, YOU_RIGHT_API_KEY, BILLING_WEBHOOK_SECRET, CRON_SECRET)

## 2. Backend — FastAPI

- [x] 2.1 Создать `apps/backend/requirements.txt` с зависимостями: fastapi, uvicorn[standard], sqlalchemy, psycopg2-binary, pydantic, pydantic-settings
- [x] 2.2 Создать `apps/backend/main.py` с FastAPI-приложением и эндпоинтом `GET /api/health` → `{"status": "ok"}`
- [x] 2.3 Создать `apps/backend/core/config.py` — модуль настроек на базе `pydantic-settings` (BaseSettings), читающий DATABASE_URL, ENV, SECRET_KEY из окружения
- [x] 2.4 Создать `apps/backend/Dockerfile` — multi-stage build (builder + runtime на python:3.11-slim, non-root user `appuser`, EXPOSE 8000)

## 3. Frontend — Next.js

- [x] 3.1 Создать `apps/frontend/Dockerfile` — multi-stage build (deps → builder → runner на node:20-alpine, non-root user `nextjs`, EXPOSE 3000, запуск standalone-сервера)

## 4. Docker Compose

- [x] 4.1 Создать `docker-compose.yml` в корне с сервисами `db`, `backend`, `frontend` и сетью `app-network`
- [x] 4.2 Настроить сервис `db`: образ `postgres:16-alpine`, именованный volume `postgres_data`, переменные POSTGRES_USER/PASSWORD/DB, порт 5432:5432
- [x] 4.3 Настроить сервис `backend`: build из `./apps/backend`, зависимость от `db`, переменная `DATABASE_URL`, volume `./apps/backend:/app` для hot-reload, uvicorn с `--reload`, порт 8000:8000
- [x] 4.4 Настроить сервис `frontend`: build из `./apps/frontend`, зависимость от `backend`, порт 3000:3000, переменные NEXTAUTH_URL и NEXTAUTH_SECRET

## 5. Верификация

- [x] 5.1 Выполнить `docker compose up -d` и убедиться, что все три контейнера запускаются без ошибок
- [x] 5.2 Проверить `curl http://localhost:8000/api/health` → `{"status": "ok"}`
- [x] 5.3 Проверить доступность фронтенда на `http://localhost:3000`
