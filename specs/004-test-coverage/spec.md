# Feature Specification: Test Coverage for Missing Application Tests

**Feature Branch**: `004-test-coverage`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "create a specification to create all missing tests for the application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API unit and integration test coverage (Priority: P1)

As a maintainer, I want every API module, service, router, and core utility to have
automated tests so regressions are caught before merge.

**Why this priority**: The API is authoritative; clients only consume it. Gaps here
risk data/authorization bugs reaching production.

**Independent Test**: Run `cd apps/api && uv run pytest` with coverage enabled; all
new suites pass and coverage on changed code reaches >=80%.

**Acceptance Scenarios**:

1. **Given** a module with no tests, **When** tests are added, **Then** its public
   behavior and error paths are exercised.
2. **Given** authorization boundaries, **When** tests run, **Then** unauthorized
   access is asserted to fail.

### User Story 2 - Web test coverage (Priority: P2)

As a maintainer, I want web pages, components, and auth helpers tested so UI
regressions are detected.

**Why this priority**: Web is the primary client; only a smoke test exists today.

**Independent Test**: Run `pnpm --filter @admin-template/web test` and `pnpm --filter @admin-template/web typecheck`; all pass.

**Acceptance Scenarios**:

1. **Given** a page component, **When** rendered in tests, **Then** key interactions
   work and error states render.

### User Story 3 - Mobile test coverage (Priority: P3)

As a maintainer, I want Flutter screens and auth services tested.

**Why this priority**: Mobile is a secondary client but ships to users.

**Independent Test**: Run `flutter test` in `apps/mobile`; all pass.

**Acceptance Scenarios**:

1. **Given** a screen, **When** widget tests run, **Then** rendering and navigation
   behave as expected.

### User Story 4 - Shared UI package tests (Priority: P3)

As a maintainer, I want `packages/ui` components tested for accessibility and behavior.

**Why this priority**: Shared components are consumed by web; bugs propagate.

**Independent Test**: Component tests pass under the chosen runner.

**Acceptance Scenarios**:

1. **Given** a component, **When** tested, **Then** props, variants, and a11y
   attributes behave correctly.

### Edge Cases

- What happens when external services (email, OIDC) are unavailable in tests? Mock them.
- How does the system handle missing env vars in test setup? Provide fixtures.
- What happens with tenant isolation boundaries? Assert cross-tenant denial.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add tests for every API module under `apps/api/src` lacking coverage (identity, tenancy, workspace, dashboard, items, auth, permissions, core).
- **FR-002**: System MUST add tests for API error paths and authorization boundaries, not only happy paths.
- **FR-003**: System MUST add web tests for pages in `apps/web/app` and helpers in `apps/web/lib`.
- **FR-004**: System MUST add mobile tests for screens in `apps/mobile/lib/features` and auth services.
- **FR-005**: System MUST add component tests for `packages/ui/src/components`.
- **FR-006**: System MUST keep existing tests passing; no weakening of assertions.
- **FR-007**: System MUST reach >=80% coverage on changed code.
- **FR-008**: System MUST use existing test frameworks (pytest, vitest, flutter test) without introducing new build systems.

### Key Entities

- **Test Suite**: collection of tests per workspace.
- **Coverage Report**: metric of exercised code.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `cd apps/api && uv run pytest` passes with no failures.
- **SC-002**: `pnpm --filter @admin-template/web test` passes with no failures.
- **SC-003**: `cd apps/mobile && flutter test` passes with no failures.
- **SC-004**: Coverage on changed code >=80%.
- **SC-005**: No lint/typecheck failures introduced.

## Assumptions

- Existing test infrastructure (pytest fixtures, vitest config) is reused.
- External services are mocked in tests.
- Tests run in CI without network access where possible.
- Mobile tests may require device/emulator for integration tests; widget tests run headless.