# Tasks: Standalone Machine Admin Agent

**Input**: Design documents from `/specs/001-standalone-machine-admin-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Create `apps/agent` project structure per plan.md
- [x] T002 Initialize Python project with pyproject.toml in `apps/agent/pyproject.toml`
- [x] T003 [P] Configure ruff/pyright in `apps/agent/pyproject.toml`
- [x] T004 Create Dockerfile at `apps/agent/Dockerfile`

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T005 Create core API agents module package at `apps/api/src/admin_template/modules/agents/__init__.py`
- [x] T006 [P] Create Agent model in `apps/api/src/admin_template/modules/agents/models.py`
- [x] T007 [P] Create AgentSession model in `apps/api/src/admin_template/modules/agents/models.py`
- [x] T008 [P] Create AuditEntry model in `apps/api/src/admin_template/modules/agents/models.py`
- [x] T009 Create Alembic migration for agent tables in `apps/api/migrations/versions/`
- [x] T010 Create agent service in `apps/api/src/admin_template/modules/agents/service.py`
- [x] T011 Create agent router in `apps/api/src/admin_template/modules/agents/router.py`
- [x] T012 Wire agent router in `apps/api/src/admin_template/api/main.py`
- [x] T013 [P] Create agent daemon entrypoint in `apps/agent/src/admin_template_agent/main.py`
- [x] T014 [P] Create agent config in `apps/agent/src/admin_template_agent/config.py`
- [x] T015 [P] Create agent auth in `apps/agent/src/admin_template_agent/auth.py`

## Phase 3: User Story 1 - Connect to local agent and chat (Priority: P1)

**Goal**: Default agent on server; web chat works.
**Independent Test**: Start agent, send chat, receive stream.

- [x] T016 [US1] Implement Pydantic AI agent core in `apps/agent/src/admin_template_agent/agent/core.py`
- [x] T017 [P] [US1] Implement filesystem tool in `apps/agent/src/admin_template_agent/agent/tools/filesystem.py`
- [x] T018 [P] [US1] Implement shell tool in `apps/agent/src/admin_template_agent/agent/tools/shell.py`
- [x] T019 [US1] Implement chat streaming endpoint in `apps/agent/src/admin_template_agent/routers/chat.py`
- [x] T020 [US1] Implement session persistence in `apps/agent/src/admin_template_agent/session.py`
- [x] T021 [US1] Web agent selector component in `apps/web/components/agent-selector.tsx`
- [x] T022 [US1] Web chat page targeting agent in `apps/web/app/agents/[id]/page.tsx`
- [x] T023 [US1] Update web chat component to use selected agent in `apps/web/components/chat.tsx`

## Phase 4: User Story 2 - Register remote agent (Priority: P2)

**Goal**: Register and health-check remote agents.
**Independent Test**: Register by URL+token, verify health, chat.

- [x] T024 [US2] Implement registry CRUD service in `apps/api/src/admin_template/modules/agents/service.py`
- [x] T025 [US2] Implement registry router endpoints in `apps/api/src/admin_template/modules/agents/router.py`
- [x] T026 [US2] Health check background task in `apps/api/src/admin_template/modules/agents/health.py`
- [x] T027 [US2] Web agents management page in `apps/web/app/agents/page.tsx`
- [x] T028 [US2] Web register agent form in `apps/web/components/register-agent-form.tsx`

## Phase 5: User Story 3 - Approve destructive actions (Priority: P3)

**Goal**: Approval gates and audit log.
**Independent Test**: Destructive request requires approval and audit entry.

- [x] T029 [US3] Implement tool guardrails in `apps/agent/src/admin_template_agent/agent/guardrails.py`
- [x] T030 [US3] Implement audit logging in `apps/agent/src/admin_template_agent/audit.py`
- [x] T031 [US3] Implement audit persistence in `apps/api/src/admin_template/modules/agents/audit.py`
- [x] T032 [US3] Web approval dialog in `apps/web/components/approval-dialog.tsx`
- [x] T033 [US3] Web audit log view in `apps/web/app/agents/audit/page.tsx`

## Final Phase: Polish & Cross-Cutting Concerns

- [x] T034 [P] MCP client integration in `apps/agent/src/admin_template_agent/mcp.py`
- [x] T035 [P] Skills loader in `apps/agent/src/admin_template_agent/skills.py`
- [x] T036 [P] Mobile agent list screen in `apps/mobile/lib/features/agents/agent_list_screen.dart`
- [x] T037 [P] Mobile chat screen in `apps/mobile/lib/features/agents/agent_chat_screen.dart`
- [x] T038 Documentation updates in `docs/agent.md`
- [x] T039 Run quickstart validation

## Dependencies

- Phase 2 blocks all user stories.
- US2 depends on US1 agent daemon.
- US3 depends on US1 tools.
## Phase 6: Convergence

- [x] T040 Restore `apps/api/src/admin_template/modules/agents/` package with Agent, AgentSession, and AuditEntry models per data-model.md (missing)
- [x] T041 Restore Alembic migration for agent tables in `apps/api/migrations/versions/` (missing)
- [x] T042 Restore registry CRUD service with tenant isolation in `apps/api/src/admin_template/modules/agents/service.py` (missing)
- [x] T043 Restore agent router endpoints and wire into `apps/api/src/admin_template/api/main.py` and v1 router (missing)
- [x] T044 Restore periodic health check background task in `apps/api/src/admin_template/modules/agents/health.py` (missing)
- [x] T045 Restore audit persistence in `apps/api/src/admin_template/modules/agents/audit.py` (missing)
- [x] T046 Provision default local agent on self-hosted servers per FR-010 (missing)
- [x] T047 Re-add any agent-related API dependencies removed from `apps/api/pyproject.toml` (partial)
## Phase 7: Convergence

- [x] T048 Enforce RBAC on agent management endpoints per FR-009 (contradicts, CRITICAL)
  - Add `require_roles(TenantRole.ADMIN, TenantRole.OWNER)` to POST/DELETE/PATCH agent endpoints in `apps/api/src/admin_template/modules/agents/router.py`; currently only `get_current_user_from_session` is applied, allowing any authenticated user to register/delete agents. Constitution Article VI requires authorization enforcement at server-side boundaries and tenant isolation across APIs.
- [x] T049 Add role-based authorization on agent daemon `PUT /config` per FR-009 (partial, HIGH)
  - The daemon config endpoint (`apps/agent/src/admin_template_agent/routers/chat.py:110`) accepts only a bearer token; extend it to require an admin role before allowing runtime mutation of `allow_shell`, `require_approval_for_destructive`, and model settings.
- [x] T050 Add audit latency assertion per SC-004 (partial, HIGH)
  - SC-004 requires all tool invocations appear in the audit log within 1 second. No test currently enforces this. Add a regression test that records an audit entry and asserts the persisted `created_at` is within 1 second of the call.
- [x] T051 Wire `ApprovalDialog` into the chat UI per US3/AC1 (partial, HIGH)
  - `components/approval-dialog.tsx` exists but is never imported or rendered by `chat.tsx` or `chat-page-client.tsx`. Connect the dialog to surface pending approvals from the agent daemon's `pending_approval` audit entries so the user can approve/deny destructive tool calls.
- [x] T052 Create `apps/agent/deploy/` manifests per plan.md (missing, MEDIUM)
  - `plan.md:55` lists `deploy/` under `apps/agent/` but the directory does not exist. Create `docker-compose.yml` and/or Kubernetes manifests for the standalone agent daemon.
- [x] T053 Emit `first_token_ms` in SSE stream per SC-002 (partial, MEDIUM)
  - SC-002 requires 95% of chat requests return first token within 3 seconds, but the SSE stream (`apps/agent/src/admin_template_agent/routers/chat.py`) emits only `{delta, error}`. Add a `first_token_ms` field to the first event and emit a `latency_ms` summary on completion.
- [x] T054 Wire mobile agent screens to the real registry API per US1/US2 (partial, LOW)
  - `agent_list_screen.dart:29` and `agent_chat_screen.dart:33` contain `TODO: wire to real API client` and use hardcoded `Future.delayed` mock data. Replace with HTTP calls to the agent registry API.
- [x] T055 Extend `PUT /config` allowed keys per FR-008 (partial, LOW)
  - FR-008 requires configuring model, prompt, tools, MCP servers, and skills. The daemon config endpoint (`routers/chat.py:110`) only accepts `model`, `model_provider`, `allow_shell`, `require_approval_for_destructive`. Extend the allowed keys to include `mcp_servers`, `skills`, `prompt`, and `tools`.
## Phase 8: Convergence

- [x] T056 Wire agent daemon audit records to the core API per FR-007/SC-004 (contradicts, CRITICAL)
  - `apps/agent/src/admin_template_agent/audit.py:6` now POSTs each audit entry to the core API (`config.api_url` + `config.api_token` Bearer auth) and calls `update_audit_status` on completion. Verified by `apps/agent/tests/test_audit.py`.
- [x] T057 Implement approval round-trip on the agent daemon per FR-006/US3/SC-003 (missing, CRITICAL)
  - `apps/agent/src/admin_template_agent/approvals.py` provides `ApprovalRegistry` + `new_registry()`. `apps/agent/src/admin_template_agent/agent/core.py` logs `pending_approval`, emits `approval_request` SSE events, and awaits the human decision via `POST /approve/{id}` before executing destructive tools. Verified by `apps/agent/tests/test_approvals.py`.
- [x] T058 Provision default agent on startup/tenant creation per FR-010 (missing, HIGH)
  - `apps/api/src/admin_template/api/main.py:41-55` calls `agent_service.provision_default_agent(tenant.id)` on startup when `settings.provision_default_agent` is set.
- [x] T059 Send stored agent token on health probes per FR-003 (partial, HIGH)
  - `apps/api/src/admin_template/modules/agents/router.py:364-366` now sends `Authorization: Bearer <token>` using the agent's stored token (falls back to `registration_token`), with a token-less retry on 401/403.
- [x] T060 Add first-token latency test per SC-002 (partial, MEDIUM)
  - `apps/agent/tests/test_sse_latency.py` asserts `first_token_ms` is emitted and under the 3-second SC-002 budget.
- [x] T061 Add RBAC enforcement test per FR-009 / Constitution Article VI (partial, MEDIUM)
  - `apps/api/tests/unit/test_agents_rbac.py` (6 tests) asserts 403 for MEMBER/VIEWER on POST/PATCH/DELETE and 201/204 for OWNER/ADMIN. All green.
- [x] T062 Persist agent chat sessions to the `AgentSession` table per FR-001 / plan data model (partial, LOW)
  - `apps/agent/src/admin_template_agent/session.py` accepts an optional `persistence` callback that forwards `(session_id, role, content)` to the core API's `AgentSession` table (FR-001).
- [x] T063 Handle approval SSE events in the mobile chat screen per US3 (partial, LOW)
  - `apps/mobile/lib/features/agents/agent_chat_screen.dart:111,174` parses `approval_request` events from the SSE stream and POSTs to `/approve/$approvalId`.
