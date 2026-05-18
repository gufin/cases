## ADDED Requirements

### Requirement: Базовая структура директорий монорепозитория
Репозиторий SHALL содержать директории `apps/backend`, `apps/frontend` и `docker` в корне. В корне также SHALL присутствовать `.gitignore` с исключениями для `__pycache__`, `.env`, `node_modules`, `.next`.

#### Scenario: Клонирование репозитория
- **WHEN** разработчик клонирует репозиторий
- **THEN** в корне присутствуют директории `apps/backend/`, `apps/frontend/`, `docker/`, файлы `docker-compose.yml` и `.env.example`

#### Scenario: Защита секретов
- **WHEN** разработчик выполняет `git status` после создания `.env`
- **THEN** файл `.env` не отображается как неотслеживаемый (находится в `.gitignore`)
