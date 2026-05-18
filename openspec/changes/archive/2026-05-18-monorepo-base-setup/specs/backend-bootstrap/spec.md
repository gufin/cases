## ADDED Requirements

### Requirement: FastAPI-приложение с health-эндпоинтом
`apps/backend/main.py` SHALL определять FastAPI-приложение с эндпоинтом `GET /api/health`, который возвращает JSON `{"status": "ok"}` со статус-кодом 200.

#### Scenario: Успешный health-check
- **WHEN** клиент выполняет `GET /api/health`
- **THEN** сервер возвращает `200 OK` и тело `{"status": "ok"}`

### Requirement: Конфигурация через pydantic-settings
`apps/backend/` SHALL содержать модуль настроек на базе `pydantic-settings`, читающий переменные окружения, включая `DATABASE_URL`, `ENV`, `SECRET_KEY`.

#### Scenario: Чтение DATABASE_URL из окружения
- **WHEN** переменная окружения `DATABASE_URL` установлена
- **THEN** настройки приложения содержат корректный DSN без хардкода

### Requirement: requirements.txt с зафиксированными зависимостями
`apps/backend/requirements.txt` SHALL содержать: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg2-binary`, `pydantic`, `pydantic-settings`.

#### Scenario: Установка зависимостей
- **WHEN** выполняется `pip install -r requirements.txt`
- **THEN** все зависимости устанавливаются без конфликтов

### Requirement: Multi-stage Dockerfile для backend
`apps/backend/Dockerfile` SHALL использовать multi-stage build (builder + runtime), финальный образ на `python:3.11-slim`, запускать uvicorn от non-root пользователя.

#### Scenario: Сборка образа
- **WHEN** выполняется `docker build apps/backend`
- **THEN** образ собирается успешно, процесс uvicorn запускается от пользователя без root-привилегий
