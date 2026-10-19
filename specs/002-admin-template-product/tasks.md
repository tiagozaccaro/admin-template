# Tasks: Admin Template Product

**Input**: Design documents from `/specs/002-admin-template-product/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included (required by FR-020 and constitution Article IX).

**Organization**: Tasks grouped by user story for independent implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create monorepo structure per plan.md: apps/{web,mobile,api}, packages/{web-ui,web-config,api-client-ts}, mobile/packages/admin_ui, backend/src/admin_template, migrations, tests, specs, docs
- [X] T002 Initialize pnpm workspace + Turborepo config (pnpm-workspace.yaml, package.json, turbo.json)
- [X] T003 [P] Initialize Python project with uv (pyproject.toml, uv.lock) for apps/api
- [X] T004 [P] Initialize Flutter project in apps/mobile with valid Dart structure
- [X] T005 [P] Initialize Next.js 16 + TypeScript strict app in apps/web with shadcn/ui + Tailwind 4
- [X] T006 [P] Configure linting/formatting: ruff (api), eslint+prettier (web), dart format/analyze (mobile)
- [X] T007 [P] Add .env.example files for all stacks (no secrets)
- [X] T008 [P] Add CI workflow skeleton covering affected stacks in .github/workflows/

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure blocking all user stories

- [X] T009 Setup PostgreSQL + Alembic migrations framework in apps/api and migrations/
- [X] T010 Create base SQLAlchemy models and session management in backend/src/admin_template/database/
- [X] T011 [P] Implement config/settings with env validation in backend/src/admin_template/core/config.py
- [X] T012 [P] Implement structured logging + request correlation ids in backend/src/admin_template/observability/
- [X] T013 [P] Implement health/readiness endpoints in backend/src/admin_template/api/health.py
- [X] T014 Implement auth framework (JWT/session, password hashing n/a, middleware) in backend/src/admin_template/auth/
- [X] T015 [P] Implement permission/role matrix in backend/src/admin_template/permissions/
- [X] T016 [P] Implement tenancy context resolution + membership validation in backend/src/admin_template/tenancy/
- [X] T017 Implement error handling + consistent error responses + pagination conventions in backend/src/admin_template/core/
- [X] T018 [P] Create User, ExternalIdentity, Session models in backend/src/admin_template/modules/identity/models.py
- [X] T019 [P] Create Tenant, TenantMembership, Invitation models in backend/src/admin_template/modules/tenancy/models.py
- [X] T020 [P] Generate initial Alembic migration for all foundational entities in migrations/
- [X] T021 Implement OpenAPI generation + client generation scripts (packages/contracts, packages/api-client-ts)

**Checkpoint**: Foundation ready; user stories can begin.

## Phase 3: User Story 1 - Run the template (Priority: P1) 🎯 MVP

**Goal**: Reproducible setup and documented commands.

**Independent Test**: Follow docs from clean checkout, build/run all stacks and tests.

- [X] T022 [P] [US1] Write setup documentation in docs/development.md
- [X] T023 [P] [US1] Add README quickstart referencing docs
- [X] T024 [US1] Verify migration apply + health endpoint + build commands work

**Checkpoint**: US1 complete.

## Phase 4: User Story 2 - Sign in with Google (Priority: P1)

**Goal**: Secure Google OIDC on web and mobile.

**Independent Test**: Complete login/logout on both clients; protected routes redirect.

- [X] T025 [P] [US2] Implement authlib OIDC integration (discovery, PKCE, nonce, callback) in backend/src/admin_template/auth/oidc.py
- [X] T026 [P] [US2] Implement login/callback/logout endpoints in backend/src/admin_template/auth/router.py
- [X] T027 [P] [US2] Implement session creation/revocation + refresh rotation in backend/src/admin_template/auth/sessions.py
- [X] T028 [P] [US2] Implement external identity linking/unlinking in backend/src/admin_template/modules/identity/service.py
- [X] T029 [US2] Implement account-linking verification (no silent merge) in backend/src/admin_template/modules/identity/service.py
- [X] T030 [P] [US2] Web: Next.js auth flow + secure callback handling in apps/web/src/lib/auth/
- [X] T031 [P] [US2] Mobile: Flutter auth flow with secure storage + redirect handling in apps/mobile/lib/auth/
- [X] T032 [US2] Add auth integration tests (success/invalid/expired/tampered) in tests/integration/test_auth.py
- [X] T033 [US2] Add negative security tests for CSRF and session revocation

**Checkpoint**: US2 complete.

## Phase 5: User Story 3 - Switch platforms (Priority: P1)

**Goal**: Same capabilities/data across web and mobile.

**Independent Test**: Repeat core journey on both clients; identical data/authz.

- [X] T034 [P] [US3] Implement parity matrix document in docs/parity-matrix.md
- [X] T035 [US3] Add cross-platform e2e smoke tests in tests/e2e/

**Checkpoint**: US3 complete.

## Phase 6: User Story 4 - Manage tenant (Priority: P1)

**Goal**: Tenant CRUD, members, invitations, ownership transfer.

**Independent Test**: Create tenant, invite, accept, role change, remove, transfer; verify isolation.

- [X] T036 [P] [US4] Implement tenant service (create/list/switch/details/settings) in backend/src/admin_template/modules/tenancy/service.py
- [X] T037 [P] [US4] Implement membership service (add/remove/role change) in backend/src/admin_template/modules/tenancy/memberships.py
- [X] T038 [P] [US4] Implement invitation service (create/accept/revoke/expire) in backend/src/admin_template/modules/tenancy/invitations.py
- [X] T039 [P] [US4] Implement ownership transfer in backend/src/admin_template/modules/tenancy/ownership.py
- [X] T040 [P] [US4] Implement pluggable invitation delivery adapter in backend/src/admin_template/modules/tenancy/delivery.py
- [X] T041 [US4] Tenant/invitation API endpoints in backend/src/admin_template/modules/tenancy/router.py
- [X] T042 [P] [US4] Web tenant management pages in apps/web/src/app/(app)/tenants/
- [X] T043 [P] [US4] Mobile tenant management screens in apps/mobile/lib/features/tenants/
- [X] T044 [US4] Add tenant isolation + invitation tests in tests/integration/test_tenancy.py

**Checkpoint**: US4 complete.

## Phase 7: User Story 5 - Enforce roles (Priority: P1)

**Goal**: Centralized permission enforcement.

**Independent Test**: Direct API calls per role match matrix.

- [ ] T045 [P] [US5] Implement permission dependency + decorators in backend/src/admin_template/permissions/deps.py
- [ ] T046 [P] [US5] Apply permission checks to all protected endpoints
- [ ] T047 [US5] Add role enforcement negative tests in tests/integration/test_permissions.py

**Checkpoint**: US5 complete.

## Phase 8: User Story 6 - Dashboard (Priority: P1)

**Goal**: Real tenant-aware metrics and activity.

**Independent Test**: Dashboard values match backend aggregates; refresh on tenant switch.

- [ ] T048 [P] [US6] Implement dashboard aggregation service in backend/src/admin_template/modules/dashboard/service.py
- [ ] T049 [P] [US6] Implement dashboard endpoint in backend/src/admin_template/modules/dashboard/router.py
- [ ] T050 [P] [US6] Web dashboard page with cards/charts in apps/web/src/app/(app)/dashboard/
- [ ] T051 [P] [US6] Mobile dashboard screen in apps/mobile/lib/features/dashboard/
- [ ] T052 [US6] Add dashboard correctness tests in tests/integration/test_dashboard.py

**Checkpoint**: US6 complete.

## Phase 9: User Story 7 - Generic CRUD (Priority: P1)

**Goal**: Reusable search/filter/form/list/detail/CRUD patterns.

**Independent Test**: Full CRUD workflow on both clients with validation.

- [ ] T053 [P] [US7] Implement generic CRUD base service/pagination in backend/src/admin_template/core/crud.py
- [ ] T054 [P] [US7] Implement demo resource module (e.g., "items") end-to-end in backend/src/admin_template/modules/items/
- [ ] T055 [P] [US7] Web data table + form components in packages/web-ui and apps/web
- [ ] T056 [P] [US7] Mobile searchable list + detail screens in apps/mobile/lib/features/items/
- [ ] T057 [US7] Add CRUD validation/authorization tests in tests/integration/test_crud.py

**Checkpoint**: US7 complete.

## Phase 10: User Story 8 - AI chatbot (Priority: P1)

**Goal**: Provider-independent AI assistant on both clients.

**Independent Test**: Conversation completes, persists, streams; unauthorized access denied; provider failure handled.

- [ ] T058 [P] [US8] Implement provider-independent AI interface + adapter base in backend/src/admin_template/ai/provider.py
- [ ] T059 [P] [US8] Implement OpenAI-compatible adapter in backend/src/admin_template/ai/adapters/openai.py
- [ ] T060 [P] [US8] Implement conversation persistence (models + service) in backend/src/admin_template/ai/conversations.py
- [ ] T061 [P] [US8] Implement streaming endpoint with cancellation/timeouts in backend/src/admin_template/ai/router.py
- [ ] T062 [P] [US8] Web chat panel/page in apps/web/src/components/ai/ and apps/web/src/app/(app)/ai/
- [ ] T063 [P] [US8] Mobile chat screen in apps/mobile/lib/features/ai/
- [ ] T064 [US8] Add AI conversation + isolation + provider-failure tests in tests/integration/test_ai.py

**Checkpoint**: US8 complete.

## Phase 11: User Story 9 - Profile and preferences (Priority: P2)

**Goal**: Profile editing and preferences.

- [ ] T065 [P] [US9] Implement profile endpoints (display name, image, prefs) in backend/src/admin_template/modules/profile/router.py
- [ ] T066 [P] [US9] Web profile pages in apps/web/src/app/(app)/profile/
- [ ] T067 [P] [US9] Mobile profile screens in apps/mobile/lib/features/profile/
- [ ] T068 [US9] Add profile tests in tests/integration/test_profile.py

## Phase 12: User Story 10 - Notifications and audit (Priority: P2)

**Goal**: In-app notifications and audit history.

- [ ] T069 [P] [US10] Implement notification service + endpoints in backend/src/admin_template/modules/notifications/
- [ ] T070 [P] [US10] Implement audit event service + endpoints in backend/src/admin_template/modules/audit/
- [ ] T071 [P] [US10] Web notification center + audit table in apps/web
- [ ] T072 [P] [US10] Mobile notification view + audit list in apps/mobile
- [ ] T073 [US10] Add notification/audit tests in tests/integration/test_notifications_audit.py

## Phase 13: User Story 11 - Extension guide (Priority: P2)

**Goal**: Documented module pattern.

- [ ] T074 [US11] Write extension guide in docs/extension-guide.md
- [ ] T075 [US11] Add example module walkthrough

## Phase 14: User Story 12 - AI provider config (Priority: P2)

**Goal**: Swap/add provider adapter.

- [ ] T076 [P] [US12] Document provider evaluation + config in docs/ai-providers.md
- [ ] T077 [US12] Add second adapter (e.g., Anthropic) skeleton behind interface

## Phase 15: User Story 13 - AI approval (Priority: P2)

**Goal**: Explicit approval for consequential AI tools.

- [ ] T078 [P] [US13] Implement tool framework (typed schemas, validation, authz, tenant context, timeouts, audit, approval) in backend/src/admin_template/ai/tools.py
- [ ] T079 [P] [US13] Implement read-only dashboard metric tool in backend/src/admin_template/ai/tools.py
- [ ] T080 [US13] Add approval flow UI on web and mobile
- [ ] T081 [US13] Add AI tool authorization/approval tests in tests/integration/test_ai_tools.py

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple stories

- [ ] T082 [P] Update parity matrix with all entry points in docs/parity-matrix.md
- [ ] T083 [P] Accessibility pass (keyboard nav, focus, touch targets, color) on web and mobile
- [ ] T084 [P] Containerized local dev (docker-compose) in infrastructure/
- [ ] T085 [P] Production deployment reference docs in docs/deployment.md
- [ ] T086 Run quickstart.md validation end-to-end
- [ ] T087 [P] Additional unit tests across stacks
- [ ] T088 Security hardening review + negative tests
- [ ] T089 Regenerate and verify API clients

## Dependencies & Execution Order

- Phase 1 (Setup) → Phase 2 (Foundational) blocks all stories.
- US1 (run template) and US2 (auth) are P1 foundation; US4/6/7/8 depend on auth+tenancy.
- US3 (parity) spans all; complete after core journeys.
- P2 stories (US9–US13) after P1 core.
- Polish (Phase 16) last.

## Parallel Opportunities

- Setup tasks marked [P] can run in parallel.
- Foundational [P] tasks can run in parallel.
- Once foundational done, US1–US8 can proceed in parallel by different developers.
- Within each story, [P] models/services can run in parallel.

## Implementation Strategy

### MVP First (US1 + US2)
1. Complete Phase 1–2.
2. Complete US1 and US2.
3. Validate independently; deploy/demo.

### Incremental Delivery
1. Setup + Foundational → foundation ready.
2. Add US1, US2 → MVP.
3. Add US4, US5, US6, US7, US8 → P0 complete.
4. Add P2 stories → P1 complete.
5. Polish → release.

## Notes
- [P] = different files, no dependencies.
- [USn] maps to user story.
- Tests included per FR-020/constitution.
- Each story independently completable and testable.
