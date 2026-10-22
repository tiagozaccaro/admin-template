# Feature Specification: Admin Template Product

**Feature Branch**: `002-admin-template-product`
**Created**: 2026-10-18
**Status**: Draft
**Input**: User description: "Admin Template — Product Specification v1.0.0: reusable full-stack foundation (Flutter mobile + Next.js web + FastAPI backend) with Google OIDC, multi-tenant organizations, roles, dashboard, generic CRUD, notifications, audit history, typed API contracts, tests, CI, and extension guides."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the template from a clean checkout (Priority: P1)

As a developer, I want reproducible setup and documented commands so I can build and test all three stacks from a clean checkout.

**Why this priority**: Without a runnable foundation nothing else can be verified or extended.

**Independent Test**: Follow documentation from a clean checkout, configure dependencies, apply migrations, start API and web app, launch a supported mobile target, and run the documented test commands.

**Acceptance Scenarios**:

1. **Given** a clean checkout, **When** a developer follows setup docs, **Then** all three stacks install and run successfully.
2. **Given** the API running, **When** its health endpoint is requested, **Then** it returns a healthy status.
3. **Given** a clean database, **When** migrations are applied, **Then** all required tables exist with constraints.

---

### User Story 2 - Sign in with Google on both clients (Priority: P1)

As a user, I want to authenticate securely on web and mobile through Google OIDC.

**Why this priority**: Authentication gates every other capability.

**Independent Test**: Complete Google login on web and mobile, verify session creation, logout, and that protected routes redirect unauthenticated users.

**Acceptance Scenarios**:

1. **Given** a valid Google account, **When** the user signs in on web or mobile, **Then** a session is created and protected screens are accessible.
2. **Given** an authenticated session, **When** the user logs out, **Then** further protected access is denied.
3. **Given** an expired or tampered token, **When** access is attempted, **Then** the request is rejected predictably.

---

### User Story 3 - Switch platforms without losing capability (Priority: P1)

As a user, I want the same supported capabilities and data when moving between web and mobile.

**Why this priority**: Cross-platform parity is a core product principle.

**Independent Test**: Perform a core journey (e.g., view dashboard, manage a member) on web, then repeat on mobile, and confirm identical data and authorization outcomes.

**Acceptance Scenarios**:

1. **Given** a user with memberships, **When** they switch active tenant on either client, **Then** only authorized records for that tenant are shown.
2. **Given** a Viewer role, **When** they attempt a write operation on either client, **Then** it is rejected by the backend.

---

### User Story 4 - Manage tenant, members, and invitations (Priority: P1)

As a tenant owner or admin, I want to manage organizations, members, and invitations securely.

**Why this priority**: Multi-tenant administration is the core domain.

**Independent Test**: Create tenant, invite member, accept invitation, change role, remove member, transfer ownership, and verify audit records and tenant isolation.

**Acceptance Scenarios**:

1. **Given** an owner, **When** they invite a user by email, **Then** an invitation record is created with expiration.
2. **Given** an accepted invitation, **When** membership is created, **Then** the user can access the tenant with the assigned role.
3. **Given** a tampered tenant id in a request, **When** access is attempted, **Then** it fails closed.

---

### User Story 5 - Enforce roles and permissions (Priority: P1)

As a tenant owner, I want permissions to restrict actions correctly across all operations.

**Why this priority**: Authorization is a security-critical foundation.

**Independent Test**: Issue direct API calls with each role and verify allowed/denied outcomes match the role-permission matrix.

**Acceptance Scenarios**:

1. **Given** insufficient permissions, **When** a protected endpoint is called directly, **Then** it returns an authorization error.
2. **Given** a client-side role change attempt, **When** submitted, **Then** the backend rejects it.

---

### User Story 6 - Use the dashboard (Priority: P1)

As an authorized user, I want real tenant-aware metrics and recent activity.

**Why this priority**: Dashboard is the primary landing experience.

**Independent Test**: Load dashboard for a tenant with known data and verify metric values match backend aggregates, refresh on tenant switch.

**Acceptance Scenarios**:

1. **Given** a tenant with members and invitations, **When** the dashboard loads, **Then** metric cards reflect real counts.
2. **Given** a tenant switch, **When** the dashboard reloads, **Then** metrics update to the new tenant.

---

### User Story 7 - Manage resources via generic CRUD (Priority: P1)

As an authorized user, I want reusable search, filter, form, list, detail, and CRUD workflows demonstrated through real entities.

**Why this priority**: Establishes the reusable administrative pattern.

**Independent Test**: List, search, filter, view, create, update, and delete a template entity on both clients with validation and authorization.

**Acceptance Scenarios**:

1. **Given** existing records, **When** searching/filtering/paginating, **Then** correct subsets are returned.
2. **Given** invalid input, **When** submitting a form, **Then** validation errors are shown and no record is created.

---

### User Story 9 - Manage profile and preferences (Priority: P2)

As a user, I want to edit profile and preferences with changes visible on both clients.

**Acceptance Scenarios**:

1. **Given** a profile edit, **When** saved, **Then** changes persist and reflect on both platforms.

---

### User Story 10 - Review notifications and audit history (Priority: P2)

As a user, I want to review in-app notifications and audit events scoped to my tenant.

**Acceptance Scenarios**:

1. **Given** an admin action, **When** audit history is queried by an authorized user, **Then** the event appears with actor, action, target, time, tenant.
2. **Given** an unauthorized user, **When** audit history is requested, **Then** access is denied.

---

### User Story 11 - Extend the template with a documented module (Priority: P2)

As a developer, I want documentation demonstrating adding a small end-to-end resource module.

**Acceptance Scenarios**:

1. **Given** the extension guide, **When** followed, **Then** a new protected resource is added without rewriting auth or tenancy.

---

### Edge Cases

- What happens when an invitation email service is unavailable? The application reports honestly that delivery did not occur.
- How does the system handle two provider identities with the same email? They are not silently merged; explicit linking is required.
- What happens when the active tenant is removed or the user's membership revoked? Access is denied and the user is prompted to switch.
- How does the system handle cross-tenant id tampering? It fails closed.
- What happens on provider failure during streaming? Partial content and error state are shown; the rest of the dashboard remains usable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST provide reproducible dependency installation for all three stacks, documented run/test commands, environment-driven config, local PostgreSQL setup, a working API health endpoint, formatting/linting/type-check/test commands, CI, and architecture/contribution docs.
- **FR-002**: Web and mobile MUST implement the same supported capabilities, authorization semantics, data operations, and core user journeys, tracked in a maintained parity matrix.
- **FR-003**: The web app MUST use shadcn/ui as its primary component foundation with reusable patterns for buttons, inputs, selects, checkboxes, forms, dialogs, sheets, popovers, dropdowns, cards, tables, lists, detail views, tabs, breadcrumbs, navigation, toasts, alerts, progress, loading, pagination, search, filtering, confirmation, theme switching, and responsive layouts. Flutter MUST implement equivalent reusable widgets and theme tokens.
- **FR-004**: Google OIDC MUST be the first fully supported external login provider, with secure callbacks, session lifecycle, external identity records, safe linking/unlinking, extensible provider abstraction, PKCE where appropriate, and server-side secret retention.
- **FR-005**: Users MUST have a profile area covering display name, profile image, email/verification status, linked providers, personal preferences, theme/locale, and security info, distinguishing provider-managed from editable attributes.
- **FR-006**: The system MUST support users in multiple tenants and tenants with multiple users, with tenant creation, listing/switching, details/settings, member list/details, invitations with acceptance/revocation/expiration, member removal, secure ownership transfer, and tenant-scoped data.
- **FR-007**: Default roles MUST be Owner, Admin, Member, Viewer with a centralized role-permission matrix and server-side enforcement for protected pages/resources, user/membership management, role assignment, tenant settings, CRUD/exports, and audit history.
- **FR-008**: The dashboard MUST provide summary metric cards, recent activity, relevant resources, optional charts, date-range filtering, loading/empty/failure states, and tenant/permission-aware content computed from real data.
- **FR-009**: The template MUST provide reusable patterns for search, filtering, sorting, pagination, web tables, mobile searchable lists/detail screens, create/edit forms, client/server validation, destructive confirmation, empty/no-results states, loading/success/error feedback, detail views, consistent API error mapping, and optional bulk actions, demonstrated through real entities.
- **FR-010**: Settings MUST distinguish personal preferences, tenant settings, and operator-only config, including profile preferences, theme, tenant metadata, and configurable branding, with secrets outside user-editable settings.
- **FR-011**: The app MUST provide in-app notifications with read/unread status, tenant-scoped event visibility, clear timestamps/descriptions, and a consistent mechanism for future delivery channels, with email/push/real-time identified as implemented or future.
- **FR-012**: The system MUST record significant admin/security events (auth, linking, membership, role/permission, settings, ownership transfers/removals) with actor, action, target, time, tenant context, safe result summary, without logging secrets or unnecessary personal data, and without unauthorized modification.
- **FR-013**: FastAPI MUST expose a documented, versioned REST/JSON API with typed Pydantic models, consistent errors, appropriate status codes, input validation, pagination conventions, auth/authz dependencies, request ids/structured diagnostics, and OpenAPI docs; TypeScript and Dart clients SHOULD be generated.
- **FR-014**: PostgreSQL MUST persist data with Alembic migrations covering users, external_identities, sessions, tenants, tenant_memberships, invitations, user_preferences, tenant_settings, notifications, audit_events, with defined ownership, uniqueness, relationships, indexing, retention, deletion, tenant scope.
- **FR-015**: The architecture MUST support background work (invitation/notification delivery, scheduled cleanup) with retry, idempotency, failure reporting, observability; a separate worker only when actual processing need exists.
- **FR-016**: The project MUST provide environment-based config, example env files without secrets, PostgreSQL/migration instructions, health/readiness endpoints, structured logs, build instructions, containerized local dev option, documented production deployment reference, secret-management guidance, and CI workflows; missing optional integrations must not crash unrelated features.
- **FR-017**: Tests MUST cover Python domain/API behavior, migrations/persistence, auth/session lifecycle, tenant isolation/role enforcement, dashboard correctness, CRUD/settings/invitation flows, Flutter unit/widget/integration tests, web component/e2e tests, and critical cross-platform journeys, with CI covering affected stacks.
- **FR-018**: Developers MUST be able to change branding/theme, add a protected web page and mobile screen, add a backend module/endpoint, add a persistence model/migration, define permissions, add a resource workflow, generate/update API clients, and preserve parity/security while extending.

### Key Entities

- **User**: Internal identity with profile attributes and preferences.
- **ExternalIdentity**: Link between an internal user and a provider identity.
- **Session**: Authenticated session reference with expiration.
- **Tenant**: Organization with settings and members.
- **TenantMembership**: User-tenant association with role.
- **Invitation**: Pending membership invitation with expiration/revocation.
- **UserPreferences**: Personal theme/locale/preferences.
- **TenantSettings**: Tenant metadata and branding.
- **Notification**: In-app tenant/user-scoped event record.
- **AuditEvent**: Immutable record of significant actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can set up the project from a clean checkout using documented steps.
- **SC-002**: The web app, API, and supported mobile targets build and launch.
- **SC-003**: Google login and logout work on both clients.
- **SC-004**: Tenant and role restrictions are enforced by the backend and verified by negative tests.
- **SC-005**: Core administrative operations have equivalent supported functionality on web and mobile.
- **SC-006**: The dashboard displays real, correctly scoped data that refreshes on tenant/filter change.
- **SC-007**: CRUD workflows include validation and authorization on both clients.
- **SC-008**: Generated API contracts can be reproduced from the documented source.
- **SC-009**: CI verifies backend, web, and mobile quality gates.
- **SC-010**: A developer can add a resource-management module without rewriting foundational auth or tenancy.

## Assumptions

- Google OIDC is the only fully supported external provider in the initial release; additional providers are extensible but not required.
- Mobile operating systems, exact session architecture, OIDC implementation, state-management and cache strategies, invitation delivery, deployment target, worker necessity, and workspace layout are resolved during planning with documented rationale.
- Email/push/real-time notification channels beyond in-app are future work unless explicitly implemented.
- A background worker is introduced only when an implemented feature requires it.
- Generated clients are not manually modified in ways that disappear on regeneration.
- Performance optimization is driven by measurements; no premature optimization targets are set.
- Demo metrics are clearly labeled and not mistaken for real data.
