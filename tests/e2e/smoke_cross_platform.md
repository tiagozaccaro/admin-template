# Cross-Platform E2E Smoke Tests (US3)

## Purpose
Verify feature parity and core cross-platform journeys per the Parity Matrix (docs/parity-matrix.md). These smoke tests confirm equivalent capabilities, authorization, and data behavior on web and mobile.

## Test Environment Requirements
- Backend API running (FastAPI) with test fixtures
- Web app running (Next.js dev/preview)
- Mobile app test environment (instrumented tests)
- PostgreSQL test database (isolated)

## Smoke Test Scenarios

### SMK-001: Auth flow works on both platforms
- **Given**: Fresh session, no auth cookies/tokens
- **When**: Start Google OIDC login on web
- **Then**: Redirects to authorization URL; callback completes and establishes session
- **When**: Start login on mobile
- **Then**: Authorization URL obtained; callback handles tokens and establishes session
- **Verify**: Same auth semantics, PKCE, CSRF protection enforced on both

### SMK-002: Protected routes redirect unauthenticated users on both platforms
- **Given**: Unauthenticated state
- **When**: Access dashboard on web
- **Then**: Redirected to login
- **When**: Access dashboard/home on mobile
- **Then**: Redirected to login screen
- **Verify**: Consistent unauthorized handling

### SMK-003: Authenticated access loads profile on both platforms
- **Given**: Authenticated session
- **When**: Fetch `/me` from web client
- **Then**: Returns user profile with tenant memberships
- **When**: Fetch `/me` from mobile client
- **Then**: Returns equivalent profile data
- **Verify**: Same data shape and authorization

### SMK-004: Tenant isolation behavior is consistent
- **Given**: User belongs to multiple tenants (if present) or single tenant
- **When**: Switch tenant context on web
- **Then**: Data scoped to selected tenant only
- **When**: Switch tenant context on mobile
- **Then**: Data scoped to selected tenant only
- **Verify**: Cross-tenant access fails closed on both (server-enforced)

### SMK-005: Role restrictions enforced consistently
- **Given**: Users with different roles (Owner/Admin/Member/Viewer)
- **When**: Attempt protected operations per role on web
- **Then**: Allowed/denied according to permission matrix
- **When**: Attempt same operations on mobile
- **Then**: Same allow/deny results
- **Verify**: UI reflects permissions; backend enforces (defense in depth)

### SMK-006: Error handling parity
- **Given**: Invalid input/unauthorized requests
- **When**: Submit invalid form on web
- **Then**: Consistent error messages from API
- **When**: Submit invalid form/action on mobile
- **Then**: Consistent error messages
- **Verify**: Same validation and error response semantics

### SMK-007: Core data consistency across platforms
- **Given**: Data created via API
- **When**: View on web
- **Then**: Same data displayed
- **When**: View on mobile
- **Then**: Same data displayed
- **Verify**: Field names, values, formatting consistent per contracts

## Implementation Notes
- Cross-platform smoke tests can be implemented as:
  1. API contract/integration tests validating parity invariants (preferred for deterministic testing)
  2. Playwright E2E for web + Flutter integration tests for mobile with shared fixtures
  3. Shared test data and scenarios to ensure identical expectations

- Tests focus on capability parity, not pixel-perfect UI. Authorization, business rules, and data operations must match exactly.

## Acceptance Criteria
- [ ] All 7 smoke test scenarios documented and executable
- [ ] Web: E2E smoke tests pass
- [ ] Mobile: Integration/smoke tests pass
- [ ] API: Parity validation tests pass
- [ ] No parity regressions introduced by feature work

## References
- docs/parity-matrix.md (T034)
- specs/002-admin-template-product/contracts/openapi.yaml
- tests/integration/test_auth.py (auth baseline)

## Auth lifecycle (added)
- Register new user -> verify email -> login -> reset password -> delete account
- Signup form validation errors shown
- Protected routes redirect unauthenticated users
