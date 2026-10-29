# Feature Specification: Standalone Machine Admin Agent

**Feature Branch**: `001-standalone-machine-admin-agent`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Standalone machine admin agent service with registry, MCP, and skills, installable on multiple machines, with web/mobile connecting to multiple agents."

## User Scenarios & Testing

### User Story 1 - Connect to a local agent and chat (Priority: P1)

An administrator opens the web app, sees the default agent on the server, and chats with it to get help managing users and tenants.

**Why this priority**: Delivers immediate value; core MVP.

**Independent Test**: Can be tested by starting the default agent and sending a chat message from the web UI, receiving a streamed response.

**Acceptance Scenarios**:
1. Given a running default agent, When the admin opens the chat page, Then the agent appears in the selector and responds to messages.
2. Given an agent is offline, When the admin views the list, Then it shows as unavailable.

### User Story 2 - Register a remote agent (Priority: P2)

An administrator installs the agent on another machine and registers it in the app, then chats with it.

**Why this priority**: Enables multi-machine administration.

**Independent Test**: Register an agent by URL+token, verify health, then chat.

**Acceptance Scenarios**:
1. Given valid URL and token, When registering, Then the agent appears in the list with healthy status.
2. Given invalid token, When registering, Then registration is rejected with clear error.

### User Story 3 - Approve destructive actions (Priority: P3)

An administrator asks the agent to delete a user; the agent proposes the action and requires explicit approval before executing.

**Why this priority**: Safety for destructive ops.

**Independent Test**: Request a destructive tool; verify approval prompt and audit log.

**Acceptance Scenarios**:
1. Given a destructive request, When the agent plans the action, Then an approval prompt appears and nothing executes until approved.
2. Given approval, When executed, Then an audit record is created.

### Edge Cases
- Agent becomes unreachable mid-session: show error and allow retry.
- Conflicting agent names: enforce unique names per tenant.
- Token rotation: support updating token without re-registering.

## Requirements

### Functional Requirements
- **FR-001**: System MUST provide a standalone agent service installable on any machine.
- **FR-002**: System MUST allow registering multiple agents per tenant.
- **FR-003**: System MUST perform periodic health checks on registered agents.
- **FR-004**: Users MUST be able to select which agent to chat with.
- **FR-005**: System MUST stream chat responses from the selected agent.
- **FR-006**: System MUST require approval for destructive tool actions.
- **FR-007**: System MUST record an audit log of tool invocations.
- **FR-008**: System MUST support configuring agent model, prompt, tools, MCP servers, and skills.
- **FR-009**: System MUST enforce role-based access for agent management and tool use.
- **FR-010**: System MUST provide a default local agent on self-hosted servers.

### Key Entities
- **Agent**: name, url, token, capabilities, tenant, health status.
- **Session**: conversation history tied to user, tenant, agent.
- **AuditEntry**: actor, agent, tool, args, result, timestamp.

## Success Criteria

### Measurable Outcomes
- **SC-001**: An administrator can register a remote agent and start chatting within 2 minutes.
- **SC-002**: 95% of chat requests return first token within 3 seconds.
- **SC-003**: Destructive actions cannot execute without explicit approval.
- **SC-004**: All tool invocations appear in the audit log within 1 second.

## Assumptions
- Agents are reachable over HTTPS from the client or via the core API proxy.
- Administrators have permission to install software on target machines.
- Default agent runs on the same host as the core API in self-hosted setups.