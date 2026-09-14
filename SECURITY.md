# Security Policy

## Authentication
- Access tokens are short-lived and signed with a dedicated JWT secret.
- Refresh tokens are rotated through a separate secret and are rejected when revoked.
- Logout invalidates the current token via the JWT blocklist.
- Protected routes require authentication and reject invalid or expired tokens.
- User accounts are authorized at the resource level so users cannot access other users' posts.

## Password security
- Passwords are never stored in plaintext.
- Passwords are hashed using Argon2 via the PasswordHasher implementation.
- Password complexity requirements enforce length and character diversity.

## Encryption
- Reversible encryption is reserved for genuinely sensitive fields only.
- Encryption keys are expected to come from environment variables and must never be committed to source control.
- Passwords remain hashed, never encrypted.

## API security
- JSON request validation is enforced for write operations.
- Maximum request sizes are enforced globally.
- CORS is restricted to an allowlist.
- Security headers are applied to every response.
- HTTP 401/403/404/413/429/500 responses use consistent, user-safe payloads.

## CORS
- Only the configured application origins are allowed.
- Credentials are enabled only for the allowlisted API origins.

## Rate limiting
- Default API rate limiting is enabled and returns a 429 response when thresholds are exceeded.
- Generation endpoints are limited per user and by overall request volume.

## Input validation
- User-generated input is sanitized and checked for prompt injection patterns.
- Required payload fields are validated before AI processing.
- Oversized inputs are rejected early.

## AI security
- System instructions are separated from user data.
- User prompts cannot override the system-level AI rules.
- Maximum input and output size limits are enforced.
- AI requests time out and fail safely when the service is unavailable.
- Per-user generation limits are applied to reduce abuse and cost risk.

## Secret management
- Secrets live in environment variables, not source code or Dockerfiles.
- Secrets such as JWT keys, encryption keys, AI API keys, and database passwords must never be exposed in logs or responses.

## Database security
- Foreign keys and indexes are defined in the data models.
- User-scoped queries ensure resource ownership checks for generated and saved posts.
- Database credentials must come from environment variables.

## Reporting vulnerabilities
- Please report suspected security issues privately to the project maintainer.
- Do not publicly disclose vulnerabilities before they are triaged and fixed.
