# Plan: Test Coverage for Missing Application Tests

**Feature**: 004-test-coverage

## Technical Context

- API: pytest + coverage (uv), fixtures in apps/api/tests
- Web: vitest (apps/web/vitest.config.ts)
- Mobile: flutter test
- Shared UI: to be determined (vitest + testing-library recommended)

## Touch Points

- apps/api/tests/ — add unit/integration tests per module
- apps/web/__tests__/ and co-located tests
- apps/mobile/test/
- packages/ui — add test runner config + tests

## Phases

1. API module tests (identity, tenancy, workspace, dashboard, items, auth, permissions, core)
2. Web page/component/helper tests
3. Mobile screen/auth service tests
4. Shared UI component tests

## Constraints

- No new build systems; reuse existing frameworks.
- Mock external services.
- >=80% coverage on changed code.