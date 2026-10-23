# Feature Specification: Complete the Basic SaaS Foundation

**Feature Branch**: `003-basic-saas-foundation`
**Created**: 2026-10-23
**Status**: Draft
**Input**: User description: "Complete the Basic SaaS Foundation — analyze the existing repository and define a specification implementing only missing, incomplete, or incorrectly implemented features."

## Executive Summary and Current-State Assessment

The repository is a multi-stack admin template (Next.js 16 web, Flutter mobile, FastAPI backend) with OIDC (Keycloak/Google) foundations, multi-tenant organizations, RBAC roles, dashboard, generic CRUD (items), notifications, audit events, and Alembic migrations. Much of the intended product (spec 002) is partially implemented; several capabilities are placeholders, incomplete workflows, or lack verification. This specification targets only the gaps that prevent the project from serving as a reusable, production-oriented basic SaaS foundation, preserving existing architecture and conventions.

Current strengths (evidence: `apps/api/src/admin_template/modules/*`, `apps/web/app/*`, `deploy/*`): OIDC router, identity/tenancy/workspace modules, items CRUD, dashboard service, notifications, audit. Gaps identified below.

## Clarifications

### Session 2026-10-23

- Q: Should the foundation support local email/password registration and password recovery in addition to OIDC? → A: Yes — add local email/password registration, verification, and reset flows now.
- Q: How should account deletion handle a user's associated data? → A: Soft-delete/anonymize user; retain audit events with anonymized actor.
- Q: Should transactional emails be actually delivered or simulated? → A: Pluggable abstraction with no-op/log default plus documented real provider config.
- Q: Should full platform admin be implemented now or deferred? → A: Minimal operator health/config now; full platform admin deferred to P2.
- Q: What default expiration should organization invitations use? → A: 7 days, revocable and reissuable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete authentication lifecycle (Priority: P1)
As a user, I want registration, login, logout, email verification, and password recovery so I can securely access the platform.

**Why this priority**: Authentication gates all functionality; current login is a cookie dev placeholder on web.
**Independent Test**: Register, verify email, login, logout, reset password end-to-end.
**Acceptance Scenarios**:
1. Given a new user, When they register with valid email/password, Then an account is created and verification email sent.
2. Given an unverified account, When login attempted, Then access is blocked with clear guidance.
3. Given a reset request, When valid token submitted, Then password updates and old sessions invalidated.

### User Story 2 - Tenant isolation and authorization (Priority: P1)
As a platform user, I want strict tenant data isolation and server-side role enforcement.

**Why this priority**: Security-critical; cross-tenant leakage is unacceptable.
**Independent Test**: Issue direct API calls across tenants/roles; verify denials.
**Acceptance Scenarios**:
1. Given a user in tenant A, When they request tenant B resources by id, Then 403/404 returned.
2. Given a Member, When they attempt Admin-only actions, Then denied.
3. Given an owner departure, When no other owner, Then transfer or block enforced.

### User Story 3 - Invitations lifecycle (Priority: P1)
As an owner/admin, I want invitations with acceptance, expiration, revocation.

**Acceptance Scenarios**:
1. Given an invitation, When expired, Then acceptance fails.
2. Given revocation, When acceptance attempted, Then fails.

### User Story 4 - Application shell and UX states (Priority: P2)
As a user, I want consistent navigation, loading/error/empty states, responsive layout, theme support.

### User Story 5 - Platform administration (Priority: P2)
As a platform admin, I want distinct oversight capabilities with audit, without tenant data access by default.

### User Story 6 - Billing readiness (Priority: P3, optional)
Modular subscription/entitlement scaffolding without paid provider dependency.

### Edge Cases
- Invitation email service unavailable: report failure honestly.
- Two provider identities same email: no silent merge.
- Active tenant removed: deny access, prompt switch.
- Cross-tenant id tampering: fail closed.

## Requirements *(mandatory)*

### Functional Requirements

- AUTH-001: System MUST support user registration and login with secure password storage (bcrypt/argon2) where local credentials are used. Rationale: current OIDC-only; local dev placeholder login exists. Evidence: `apps/web/app/login`, `apps/api/src/admin_template/auth`.
- AUTH-002: System MUST provide secure session management and logout invalidating sessions. Evidence: `sessions.py`.
- AUTH-003: System MUST support email verification flow (send token, verify endpoint, block unverified). 
- AUTH-004: System MUST support password recovery and reset with time-limited, single-use tokens.
- AUTH-005: System MUST retain OAuth (Google/Keycloak) support already implemented; no regression.
- AUTH-006: System MUST provide user profile and account settings endpoints/UI.
- AUTH-007: System MUST support account deletion with associated data handling (cascade/anonymize).
- AUTH-008: System MUST implement auth failure handling and rate limiting on auth endpoints.

- TENANT-001: System MUST support organization creation, membership, ownership. Evidence: tenancy module.
- TENANT-002: System MUST implement invitations with acceptance, expiration, revocation. Evidence: `invitations.py`.
- TENANT-003: System MUST support organization switching with explicit tenant context on protected ops.
- TENANT-004: System MUST enforce strict tenant isolation across API, DB queries, background jobs, file access.
- TENANT-005: System MUST protect against cross-tenant IDOR.
- TENANT-006: System MUST handle owner departure/transfer safely (no ownerless org without explicit handling).

- RBAC-001: System MUST define roles Owner, Admin, Member, Viewer with permission matrix. Evidence: permissions module.
- RBAC-002: System MUST enforce authorization server-side consistently.
- RBAC-003: System MUST prevent privilege escalation.
- RBAC-004: System MUST include tests for permitted/forbidden ops.

- SHELL-001: Web MUST provide consistent dashboard/navigation, responsive layout, user/org menus, settings pages, breadcrumbs, loading/error/empty/success states, form validation, destructive confirmations, accessible components, light/dark theme. Evidence: `theme-provider.tsx`, shadcn.

- SHARED-001: System MUST provide consistent CRUD patterns, search/filter/sort/pagination. Evidence: items module.
- SHARED-002: System MUST provide centralized API error handling and input validation at trust boundaries.

- BILL-001 (optional): Billing MUST be modular/optional; no paid provider dependency unless justified. Out of critical path.

- NOTIF-001: System MUST provide transactional email abstraction for verification, password reset, invitations.
- NOTIF-002: System MUST handle notification errors and duplicate processing (idempotency).

- SEC-001: Secure password storage, cookie/token/session handling, CSRF where applicable, input validation/output encoding, rate limiting, secrets config, server-side authz, audit records, safe errors.
- SEC-002: Audit records for security/membership/permission/admin actions with retention protection.

- PLAT-001: Platform admin access distinct from tenant admin; oversight where justified; suspension/reactivation if required; audit records; no accidental tenant data access.

- TEST-001: Unit/integration/authz/cross-tenant/e2e/migration/CI checks as applicable.
- DEPLOY-001: Documented env config, migrations, health/readiness, structured logging, production-safe config, backup guidance, CI/CD.

### Key Entities
- User, ExternalIdentity, Session, Tenant, TenantMembership, Invitation, UserPreferences, TenantSettings, Notification, AuditEvent (existing, extend as needed).

## Success Criteria *(mandatory)*

### Measurable Outcomes
- SC-001: All P0 security gaps have automated tests passing.
- SC-002: Cross-tenant isolation demonstrated by automated tests.
- SC-003: Auth flows (register/verify/reset) complete end-to-end.
- SC-004: 100% of in-scope requirements have acceptance criteria and tests.

## Assumptions
- Existing OIDC (Keycloak/Google) remains primary auth; local password auth is additive where needed for dev/standalone.
- Billing is optional and deferred unless product requires.
- Mobile parity tracked separately; core focus web+API.
- No rewrite; preserve conventions.

## In-Scope / Out-of-Scope
In-scope: auth lifecycle completion, tenant isolation hardening, invitation lifecycle, RBAC enforcement/tests, UX states, email abstraction, audit, platform admin basics, testing, ops docs.
Out-of-scope: paid billing provider integration, advanced permissions engine, microservices, mobile full parity beyond documented.

## Module Boundaries
- identity, tenancy, permissions, notifications, audit, platform-admin modules under `apps/api/src/admin_template/modules`.
- Web routes under `apps/web/app`.
- Shared UI in `packages/ui`.

## API Contract Changes
- Add endpoints: register, verify-email, request-reset, reset-password, profile get/update, delete-account, invitations accept/revoke, tenant switch context, platform admin endpoints (if justified), health/readiness (exists).
- Preserve existing endpoints.

## Data Model & Migrations
- Add fields/columns as needed: email_verified, password_hash (if local auth), reset tokens, invitation status/expiry, audit retention. Migrations via Alembic with data preservation.

## Security Requirements
- Enforce authz at server boundary; rate limit auth; secure cookies; CSRF for cookie sessions; no secrets in logs; tenant scoping in all queries.

## Testing Strategy
- P0: cross-tenant isolation, authz negatives, auth flows.
- Integration: API+DB.
- E2E: critical journeys.
- Migration validation.

## Implementation Batches (incremental)
1. Batch 1 (P0): Auth lifecycle + session hardening + rate limiting.
2. Batch 2 (P0): Tenant isolation + IDOR protection + tests.
3. Batch 3 (P1): Invitation lifecycle completion.
4. Batch 4 (P1): RBAC enforcement + tests.
5. Batch 5 (P1): Profile/settings + account deletion.
6. Batch 6 (P2): UX states + navigation + theme.
7. Batch 7 (P2): Email abstraction + notifications reliability.
8. Batch 8 (P2): Audit hardening + platform admin basics.
9. Batch 9 (P2): Ops docs + health/readiness + CI.
10. Batch 10 (P3, optional): Billing modular scaffolding.

## Definition of Done
- All in-scope requirements implemented with tests.
- Security tests pass.
- Migrations apply cleanly.
- Docs updated.
- No regression of existing functionality.