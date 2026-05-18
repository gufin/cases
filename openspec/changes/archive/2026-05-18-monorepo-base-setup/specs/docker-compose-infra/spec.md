## ADDED Requirements

### Requirement: docker-compose.yml с тремя сервисами
Корневой `docker-compose.yml` SHALL определять сервисы `db`, `backend`, `frontend`, объединённые в общую сеть `app-network`.

#### Scenario: Запуск всего окружения
- **WHEN** выполняется `docker compose up -d`
- **THEN** поднимаются все три контейнера, `backend` успешно подключается к `db` по hostname `db`

### Requirement: Сервис db (PostgreSQL 16)
Сервис `db` SHALL использовать образ `postgres:16-alpine`, хранить данные в именованном volume, принимать переменные `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` из `.env`.

#### Scenario: Персистентность данных
- **WHEN** контейнер `db` перезапускается
- **THEN** ранее созданные таблицы и данные сохраняются

### Requirement: Переменная DATABASE_URL пробрасывается в backend
Сервис `backend` SHALL получать переменную окружения `DATABASE_URL` в формате `postgresql://user:password@db:5432/yurayt_crm`, где `db` — hostname сервиса PostgreSQL в compose-сети.

#### Scenario: Резолюция hostname db
- **WHEN** бэкенд пытается подключиться к БД
- **THEN** hostname `db` резолвится через Docker DNS в IP контейнера PostgreSQL

### Requirement: Проброс портов
Сервис `db` SHALL пробрасывать порт 5432, `backend` — 8000, `frontend` — 3000 на хост-машину для локальной разработки.

#### Scenario: Доступность сервисов с хоста
- **WHEN** все контейнеры запущены
- **THEN** `curl http://localhost:8000/api/health` возвращает `{"status": "ok"}`

### Requirement: Hot-reload для backend в dev-режиме
Compose SHALL монтировать `./apps/backend` как volume в контейнер backend и запускать uvicorn с флагом `--reload`.

#### Scenario: Автоперезагрузка при изменении кода
- **WHEN** разработчик изменяет файл в `apps/backend/`
- **THEN** uvicorn автоматически перезапускается без пересборки образа
