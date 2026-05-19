### Requirement: Create user on first login
The system SHALL create a new `User` record when no record with the given `keycloak_sub` exists. The new record SHALL have `plan = free` and `cases_limit = 5`. The system SHALL return the newly created `User` object.

#### Scenario: First login — user does not exist
- **WHEN** validated JWT has `sub = "abc-123"` and no `User` with `keycloak_sub = "abc-123"` exists in the database
- **THEN** system inserts a new `User` with `keycloak_sub = "abc-123"`, `plan = "free"`, `cases_limit = 5` and returns the created object

#### Scenario: Concurrent first-login requests (race condition)
- **WHEN** two simultaneous requests arrive with the same `sub` and no user yet exists
- **THEN** exactly one INSERT succeeds (ON CONFLICT DO NOTHING), both requests receive a valid `User` object

### Requirement: Return existing user on subsequent logins
The system SHALL return the existing `User` record when a record with the given `keycloak_sub` already exists, without modifying any subscription fields.

#### Scenario: Returning user
- **WHEN** validated JWT has `sub = "abc-123"` and a `User` with `keycloak_sub = "abc-123"` exists with `plan = "pro"` and `cases_limit = 100`
- **THEN** system returns the existing `User` object with `plan = "pro"` and `cases_limit = 100` unchanged

### Requirement: Upsert is atomic and race-condition safe
The system SHALL perform the upsert using `INSERT … ON CONFLICT (keycloak_sub) DO NOTHING` followed by a SELECT, within a single database session.

#### Scenario: INSERT with conflict
- **WHEN** INSERT fails due to unique constraint on `keycloak_sub`
- **THEN** system performs SELECT and returns the existing row without raising an exception
