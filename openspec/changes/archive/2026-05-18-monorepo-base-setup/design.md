## Context

Проект стартует с пустого репозитория. Нужно заложить фундамент, на котором будут строиться все бизнес-фичи: структура директорий монорепозитория, локальное окружение разработки (Docker Compose), базовые точки входа для бэкенда (FastAPI) и фронтенда (Next.js 14).

Команда работает на macOS/Linux. Локальная разработка — через `docker compose up`. В production деплой через GitHub Actions + SSH + `docker compose pull && up -d`.

## Goals / Non-Goals

**Goals:**
- Создать воспроизводимое локальное окружение одной командой (`docker compose up`)
- Инициализировать FastAPI-приложение с health-эндпоинтом и правильно сконфигурированным Dockerfile
- Подготовить Dockerfile для Next.js 14
- Настроить PostgreSQL как managed-сервис в compose
- Вынести все секреты и конфигурацию в `.env` / compose environment

**Non-Goals:**
- Реализация бизнес-логики (биллинг, Keycloak, дела) — это следующие итерации
- CI/CD pipeline — отдельный change
- Миграции Alembic — подключаются после инициализации БД-моделей
- Next.js-приложение (страницы, компоненты) — отдельный change

## Decisions

### 1. Монорепозиторий без workspaces-менеджера

**Выбор:** Простая структура директорий (`apps/backend`, `apps/frontend`) без Nx/Turborepo.

**Ратionale:** На MVP с двумя приложениями накладные расходы monorepo-менеджера не оправданы. Docker Compose является единственным оркестратором на этом этапе. Если проект вырастет — добавить Turborepo несложно.

**Альтернативы:** Nx, Turborepo — избыточны для текущего масштаба.

---

### 2. Multi-stage Dockerfile для backend

**Выбор:** Двухэтапная сборка: `builder` (установка зависимостей) → `runtime` (финальный образ на `python:3.11-slim`).

**Rationale:** Соответствует `development_guidelines.docker.multi_stage_builds: true` из config.yaml. Уменьшает размер образа, не тащит build-инструменты в production.

**Non-root user:** Добавляется пользователь `appuser` в соответствии с `docker.non_root_user: true`.

---

### 3. DATABASE_URL как единственная точка конфигурации БД

**Выбор:** `DATABASE_URL=postgresql://user:password@db:5432/yurayt_crm` передаётся через compose environment из `.env`. Бэкенд читает через `pydantic-settings`.

**Rationale:** Стандартный паттерн 12-factor app. Hostname `db` — это имя сервиса в compose-сети, резолвится автоматически через Docker DNS.

---

### 4. Порты сервисов

| Сервис | Внутренний порт | Проброс на хост |
|--------|----------------|-----------------|
| db (PostgreSQL) | 5432 | 5432 |
| backend (FastAPI/Uvicorn) | 8000 | 8000 |
| frontend (Next.js) | 3000 | 3000 |

**Rationale:** Стандартные порты для соответствующих технологий; минимизируют сюрпризы при разработке.

---

### 5. Hot reload в разработке

**Выбор:** Uvicorn запускается с `--reload` через volume-маунт `./apps/backend:/app` в compose. Frontend-контейнер также монтирует исходники.

**Rationale:** Разработчик видит изменения без пересборки образа.

## Risks / Trade-offs

- **[Риск] psycopg2-binary в production** → Mitigation: для MVP достаточно; в production заменить на `psycopg2` с нативной компиляцией или `asyncpg`.
- **[Риск] Секреты в `.env` попадут в git** → Mitigation: `.env` добавляется в `.gitignore`, в репозитории хранится только `.env.example`.
- **[Trade-off] Синхронный драйвер БД на старте** → SQLAlchemy 2.0 поддерживает async; при росте нагрузки перейти на `asyncpg` + `async_sessionmaker` без изменения остальной логики.
