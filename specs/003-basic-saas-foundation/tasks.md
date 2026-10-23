# Tasks: Complete the Basic SaaS Foundation

**Input**: Design documents from `/specs/003-basic-saas-foundation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included (security-critical).

**Organization**: Tasks grouped by user story.

## Phase 1: Setup

- [x] T001 Verify project structure and dependencies (no new frameworks)
- [x] T002 [P] Configure email abstraction module location in apps/api/src/admin_template/core/email.py

## Phase 2: Foundational

- [x] T003 Add DB migration for user auth fields (password_hash, email_verified, deleted_at) in apps/api/alembic/versions/
- [x] T004 [P] Add EmailVerificationToken and PasswordResetToken models in apps/api/src/admin_template/modules/identity/models/
- [x] T005 [P] Add Invitation expiration/revocation fields migration
- [x] T006 Implement tenant context dependency in apps/api/src/admin_template/permissions/deps.py
- [x] T007 Implement rate limiting middleware in apps/api/src/admin_template/core/

## Phase 3: User Story 1 - Complete Authentication Lifecycle (P1)

**Goal**: Registration, verification, login, logout, password reset.
**Independent Test**: Register → verify → login → reset → login with new password.

- [x] T008 [P] [US1] Implement password hashing utilities in apps/api/src/admin_template/core/security.py
- [x] T009 [US1] Implement register endpoint in apps/api/src/admin_template/auth/router.py
- [x] T010 [US1] Implement verify-email endpoint
- [x] T011 [US1] Implement request-reset and reset-password endpoints
- [x] T012 [US1] Implement account deletion (soft-delete) endpoint
- [x] T013 [US1] Update web login/signup pages in apps/web/app/login and signup
- [x] T014 [P] [US1] Add auth lifecycle tests in apps/api/tests/

## Phase 4: User Story 2 - Tenant Isolation & Authorization (P1)

**Goal**: Strict tenant scoping and RBAC enforcement.
**Independent Test**: Cross-tenant access denied; role restrictions enforced.

- [x] T015 [US2] Audit all tenant-owned queries for scoping in apps/api/src/admin_template/modules/
- [x] T016 [US2] Implement IDOR protection in routers
- [x] T017 [US2] Implement ownership transfer/departure handling in tenancy/ownership.py
- [x] T018 [P] [US2] Add cross-tenant isolation tests
- [x] T019 [P] [US2] Add RBAC permission tests

## Phase 5: User Story 3 - Invitations Lifecycle (P1)

**Goal**: Acceptance, expiration (7d), revocation.
**Independent Test**: Invite → accept; expired/revoked rejected.

- [x] T020 [US3] Implement invitation expiration enforcement in invitations.py
- [x] T021 [US3] Implement revoke endpoint
- [x] T022 [US3] Implement accept endpoint with validation
- [x] T023 [P] [US3] Add invitation tests

## Phase 6: User Story 4 - Application Shell & UX (P2)

**Goal**: Consistent navigation, states, theme.
**Independent Test**: Navigate pages; verify loading/error/empty states.

- [x] T024 [P] [US4] Add loading/error/empty state components in apps/web
- [x] T025 [US4] Add breadcrumbs and responsive layout improvements
- [x] T026 [US4] Verify light/dark theme support

## Phase 7: User Story 5 - Email Abstraction & Notifications (P2)

**Goal**: Pluggable email with no-op default; reliable delivery handling.
**Independent Test**: Emails logged in dev; provider configurable.

- [x] T027 [US5] Implement email provider interface in core/email.py
- [x] T028 [US5] Implement no-op/log provider
- [x] T029 [US5] Wire verification/reset/invitation emails
- [x] T030 [P] [US5] Add duplicate-processing/idempotency tests

## Phase 8: User Story 6 - Audit & Platform Admin (P2)

**Goal**: Audit hardening; minimal operator capability.
**Independent Test**: Audit events recorded; health endpoints work.

- [x] T031 [US6] Ensure audit events for security/membership/permission actions
- [x] T032 [US6] Add anonymization on user soft-delete
- [x] T033 [US6] Verify health/readiness endpoints
- [x] T034 [P] [US6] Add audit tests

## Phase 9: Polish & Cross-Cutting

- [x] T035 Update documentation (env, migrations, ops)
- [x] T036 Run quickstart validation
- [x] T037 Final lint/typecheck/test runs

## Dependencies

- Phase 2 blocks all user stories.
- US1/US2/US3 are P1 and can run in parallel after Phase 2.
- US4/US5/US6 are P2.

## Implementation Strategy

MVP: Phase 1-5 (auth + tenant isolation + invitations). Then incremental P2.