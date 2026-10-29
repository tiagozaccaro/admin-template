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