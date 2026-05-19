### Requirement: Extract Bearer token from Authorization header
The system SHALL extract the JWT from the `Authorization: Bearer <token>` header of every protected request. If the header is absent or does not start with `Bearer `, the system SHALL return HTTP 401.

#### Scenario: Missing Authorization header
- **WHEN** request arrives without `Authorization` header
- **THEN** system returns HTTP 401 with `{"detail": "Not authenticated"}`

#### Scenario: Malformed scheme
- **WHEN** request has `Authorization: Basic abc123`
- **THEN** system returns HTTP 401 with `{"detail": "Not authenticated"}`

### Requirement: Fetch and cache JWKS from Keycloak
The system SHALL fetch public keys from `{KEYCLOAK_ISSUER}/protocol/openid-connect/certs` and cache them in process memory with a TTL of 5 minutes. After TTL expiry the system SHALL re-fetch on the next request.

#### Scenario: Successful JWKS fetch
- **WHEN** JWKS cache is empty or expired
- **THEN** system fetches `{KEYCLOAK_ISSUER}/protocol/openid-connect/certs` via async HTTP GET and stores the result with a timestamp

#### Scenario: JWKS endpoint unreachable
- **WHEN** Keycloak JWKS endpoint returns a non-2xx response or times out
- **THEN** system returns HTTP 401 with `{"detail": "Unable to fetch JWKS"}`

#### Scenario: Cache hit
- **WHEN** JWKS was fetched less than 5 minutes ago
- **THEN** system uses the cached keys without making a network request

### Requirement: Validate JWT signature and standard claims
The system SHALL validate the JWT signature using RS256 algorithm with keys from JWKS. It SHALL also validate `exp` (not expired), `iss` (equals `KEYCLOAK_ISSUER`). If any validation fails the system SHALL return HTTP 401.

#### Scenario: Valid token
- **WHEN** token has valid RS256 signature, `iss` matches `KEYCLOAK_ISSUER`, and `exp` is in the future
- **THEN** system proceeds and returns the decoded payload

#### Scenario: Expired token
- **WHEN** token `exp` claim is in the past
- **THEN** system returns HTTP 401 with `{"detail": "Token expired"}`

#### Scenario: Wrong issuer
- **WHEN** token `iss` does not equal `KEYCLOAK_ISSUER`
- **THEN** system returns HTTP 401 with `{"detail": "Invalid token"}`

#### Scenario: Invalid signature
- **WHEN** token signature does not match any key in JWKS
- **THEN** system returns HTTP 401 with `{"detail": "Invalid token"}`

### Requirement: Extract sub claim from JWT payload
The system SHALL extract the `sub` field from the decoded JWT payload. If `sub` is absent the system SHALL return HTTP 401.

#### Scenario: sub present
- **WHEN** decoded JWT contains a non-empty `sub` field
- **THEN** system passes `sub` string to the upsert layer

#### Scenario: sub absent
- **WHEN** decoded JWT does not contain `sub`
- **THEN** system returns HTTP 401 with `{"detail": "Invalid token: missing sub"}`
