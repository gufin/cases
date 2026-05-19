### Requirement: GET /api/users/me returns current user profile
The system SHALL expose a `GET /api/users/me` endpoint protected by `get_current_user` dependency. On success it SHALL return the current user's profile serialized as `UserRead` schema with HTTP 200.

#### Scenario: Authenticated request
- **WHEN** request includes valid `Authorization: Bearer <token>` header
- **THEN** system returns HTTP 200 with JSON body matching `UserRead` schema (fields: `id`, `keycloak_sub`, `email`, `plan`, `cases_limit`, `subscription_ends_at`, `created_at`)

#### Scenario: Unauthenticated request
- **WHEN** request has no `Authorization` header or an invalid token
- **THEN** system returns HTTP 401

### Requirement: Endpoint is registered under /api prefix
The system SHALL mount the users router with prefix `/api` so the full path is `/api/users/me`. This SHALL coexist with the existing `GET /api/health` endpoint.

#### Scenario: Route resolution
- **WHEN** GET request is sent to `/api/users/me`
- **THEN** FastAPI routes it to the users router handler
