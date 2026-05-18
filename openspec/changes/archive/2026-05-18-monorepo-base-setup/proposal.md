## Why

Проект «Юрайт: Дела» начинается с нуля — нет ни структуры директорий, ни контейнеров, ни базовых точек входа для бэкенда и фронтенда. Без рабочей основы монорепозитория нельзя приступить ни к одной из бизнес-фич.

## What Changes

- Создаётся базовая структура монорепозитория: `apps/backend`, `apps/frontend`, `docker/`
- В `apps/backend` инициализируется FastAPI-приложение: `requirements.txt`, `main.py` с эндпоинтом `GET /api/health`, `Dockerfile` (multi-stage, non-root user)
- В `apps/frontend` добавляется базовый `Dockerfile` для Next.js 14
- В корне создаётся `docker-compose.yml` с тремя сервисами: `db` (PostgreSQL), `backend` (FastAPI), `frontend` (Next.js)
- Настроена внутренняя Docker-сеть и проброс портов
- Переменные окружения (в т.ч. `DATABASE_URL`) вынесены из образов в compose-файл через `.env`

## Capabilities

### New Capabilities

- `monorepo-structure`: Базовая структура директорий монорепозитория (apps/backend, apps/frontend, docker)
- `backend-bootstrap`: FastAPI-приложение с health-эндпоинтом, requirements.txt и Dockerfile
- `frontend-bootstrap`: Заготовка Next.js 14 с Dockerfile
- `docker-compose-infra`: Оркестрация трёх контейнеров (db, backend, frontend) с сетью и env-переменными

### Modified Capabilities

## Impact

- Затрагивает корень репозитория (новые файлы `docker-compose.yml`, `.env.example`)
- Новые директории `apps/backend/` и `apps/frontend/`
- Зависимости: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic v2, Node.js 20 (внутри Docker)
- PostgreSQL 16 как сервис в compose
