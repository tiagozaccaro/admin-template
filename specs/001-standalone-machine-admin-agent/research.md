# Research

## Decisions

- **Agent runtime**: Pydantic AI + pydantic-ai-harness for tools (filesystem, shell, code mode, memory).
- **Transport**: FastAPI with SSE streaming; optional WebSocket later.
- **Registry**: PostgreSQL table in core API; agents register via token.
- **Auth**: Bearer token per agent; JWT for user-facing API.
- **MCP**: Use MCP client libraries to discover tools at runtime.
- **Skills**: YAML skill bundles loaded from disk/config.

## Alternatives considered

- Embedding agent in core API (rejected: need multi-machine).
- gRPC (rejected: SSE simpler for streaming tokens).