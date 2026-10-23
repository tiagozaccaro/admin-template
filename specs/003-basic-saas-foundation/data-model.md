# Data Model: Complete the Basic SaaS Foundation

## Entities (existing, extended)

- **User**: add `password_hash` (nullable for OIDC-only users), `email_verified` (bool), `deleted_at` (nullable soft-delete), `anonymized` flag.
- **EmailVerificationToken**: `id`, `user_id`, `token_hash`, `expires_at`, `used_at`.
- **PasswordResetToken**: `id`, `user_id`, `token_hash`, `expires_at`, `used_at`.
- **Tenant**: existing.
- **TenantMembership**: existing; ensure unique (user_id, tenant_id).
- **Invitation**: add `expires_at` (default +7 days), `revoked_at`, `accepted_at`, `status`.
- **AuditEvent**: existing; actor reference may be anonymized user id; retain.
- **Notification**: existing.

## State Transitions

- Invitation: pending → accepted / revoked / expired.
- User: active → soft-deleted (anonymized).

## Validation Rules

- Email unique per user (case-insensitive).
- Tokens single-use and time-limited.
- Tenant scoping on all tenant-owned entities.