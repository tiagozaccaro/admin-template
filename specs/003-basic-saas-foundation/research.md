# Research: Complete the Basic SaaS Foundation

## Decisions

### Local Authentication
- **Decision**: Add local email/password registration, verification, and reset flows alongside existing OIDC.
- **Rationale**: Improves starter usability and testability; clarifications confirmed.
- **Alternatives**: OIDC-only (rejected: limits local dev and standalone products).

### Account Deletion
- **Decision**: Soft-delete/anonymize user; retain audit events with anonymized actor.
- **Rationale**: Preserves audit integrity and compliance.
- **Alternatives**: Hard delete (rejected: breaks audit trail).

### Email Delivery
- **Decision**: Pluggable email abstraction with no-op/log default and documented real provider config.
- **Rationale**: Keeps foundation runnable without external deps while enabling production delivery.
- **Alternatives**: Mandatory real provider (rejected: adds hard dependency).

### Platform Admin
- **Decision**: Minimal operator health/config now; full platform admin deferred to P2.
- **Rationale**: Reduces scope and risk while preserving operability.
- **Alternatives**: Full admin now (rejected: scope creep).

### Invitation Expiration
- **Decision**: 7-day default, revocable and reissuable.
- **Rationale**: Balances security and UX.
- **Alternatives**: 24h (too short), 30d (too long).

### Tenant Isolation
- **Decision**: Enforce tenant scoping in all queries via dependency-injected tenant context; add cross-tenant tests.
- **Rationale**: Prevents IDOR and data leakage.
- **Alternatives**: Client-side filtering (rejected: insecure).

### RBAC
- **Decision**: Reuse existing roles (Owner/Admin/Member/Viewer) with centralized permission matrix; no complex engine.
- **Rationale**: Matches existing design and requirements.
- **Alternatives**: Configurable permissions engine (rejected: unnecessary complexity).