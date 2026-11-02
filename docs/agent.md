# Agent Daemon

The standalone agent lives in `apps/agent`. It exposes a Pydantic AI admin agent
with filesystem, shell, MCP, and skills support over HTTP, installable on any
machine and registerable with the core API.

## Architecture

```
apps/agent/
├── pyproject.toml          # uv project + deps (pydantic-ai, fastapi, mcp, pyyaml)
├── Dockerfile              # python:3.12-slim image
├── src/admin_template_agent/
│   ├── main.py             # FastAPI app + uvicorn entrypoint
│   ├── config.py           # Pydantic Settings from env
│   ├── auth.py             # Bearer token verification
│   ├── audit.py            # JSON-lines audit logging
│   ├── session.py          # In-memory session store
│   ├── mcp.py              # MCP client (SDK + HTTP fallback)
│   ├── skills.py           # Skill bundle loader (markdown + YAML frontmatter)
│   ├── agent/
│   │   ├── core.py         # Pydantic AI Agent wrapper
│   │   ├── guardrails.py   # Destructive-tool approval gates
│   │   └── tools/
│   │       ├── filesystem.py
│   │       └── shell.py
│   └── routers/
│       └── chat.py         # /health, /models, /tools, /config, /sessions, /chat
└── tests/
```

## Run locally

```bash
cd apps/agent
uv sync
uv run python -m admin_template_agent.main
```

The daemon listens on `0.0.0.0:8100` by default.

## Endpoints

| Method | Path                 | Description                          |
|--------|----------------------|--------------------------------------|
| GET    | `/health`            | Liveness probe                       |
| GET    | `/models`            | Available models                     |
| GET    | `/tools`             | Registered tools                     |
| GET    | `/config`            | Agent configuration                  |
| PUT    | `/config`            | Update configuration at runtime      |
| GET    | `/sessions/{id}`     | Conversation history for a session   |
| POST   | `/chat/agent`        | Stream a chat response as SSE        |
| POST   | `/chat`              | Non-streaming chat                   |

## Configuration

All settings are read from environment variables (or `.env`):

| Variable                        | Default            | Description                       |
|---------------------------------|--------------------|-----------------------------------|
| `AGENT_HOST`                    | `0.0.0.0`          | Bind address                      |
| `AGENT_PORT`                    | `8100`             | Bind port                         |
| `AGENT_NAME`                    | `local-agent`      | Display name                      |
| `MODEL`                         | `test`             | Pydantic AI model name            |
| `MODEL_PROVIDER`                | `openai`           | Provider identifier               |
| `MODEL_API_KEY`                 | —                  | LLM API key                       |
| `MODEL_API_BASE`                | —                  | Custom OpenAI-compatible base URL  |
| `AGENT_TOKEN`                   | —                  | Bearer token required for chat    |
| `API_URL`                       | `http://localhost:8000` | Core API URL                 |
| `API_TOKEN`                     | —                  | Token used to register with API   |
| `ALLOW_SHELL`                   | `false`            | Enable the shell tool             |
| `REQUIRE_APPROVAL_FOR_DESTRUCTIVE` | `true`         | Approval gates for destructive ops|
| `MCP_SERVERS`                   | —                  | Comma-separated MCP server URLs   |
| `SKILLS_DIR`                    | `skills`           | Directory of skill bundles        |
| `SESSION_STORE_PATH`            | `.agent-sessions.json` | Session persistence file     |
| `AUDIT_LOG_PATH`                | `audit.log`        | JSON-lines audit log              |

## Registering with the core API

```bash
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"my-agent","url":"http://localhost:8100","token":"changeme"}'
```

The core API health-checks registered agents on a 30-second interval and
exposes a chat proxy at `POST /api/v1/agents/{id}/chat` that streams SSE from
the agent daemon.

## Approval flow

Destructive tools (`shell`, `write_file`, `delete_file`) require explicit
approval. When invoked without approval, the tool returns `"approval required"`
and writes a `pending_approval` audit entry. The web UI surfaces these in the
`ApprovalDialog` component.

## Skills

Skills are markdown files (optionally with YAML frontmatter) placed in the
`skills/` directory. Each skill exposes a `name`, `description`, and optional
`triggers` list:

```yaml
---
description: Summarize git diffs
triggers: ["diff", "summarize"]
---
# Skill content...
```