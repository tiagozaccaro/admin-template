# Data Model

## Agent
- id (uuid), name (unique per tenant), url, token_hash, capabilities (json), tenant_id, status, last_seen_at, created_at.

## AgentSession
- id, agent_id, user_id, tenant_id, history (json), created_at, updated_at.

## AuditEntry
- id, tenant_id, user_id, agent_id, tool_name, args (json), result_summary, status, created_at.