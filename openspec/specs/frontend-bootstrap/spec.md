### Requirement: Dockerfile для Next.js 14
`apps/frontend/Dockerfile` SHALL использовать multi-stage build с базовым образом `node:20-alpine`, собирать Next.js-приложение (`npm run build`) и запускать standalone-сервер от non-root пользователя на порту 3000.

#### Scenario: Сборка образа frontend
- **WHEN** выполняется `docker build apps/frontend`
- **THEN** образ собирается и Next.js-сервер стартует на порту 3000 от non-root пользователя

#### Scenario: Интеграция с compose
- **WHEN** выполняется `docker compose up frontend`
- **THEN** сервис `frontend` доступен на `http://localhost:3000`
