# Implementation Plan: Standalone Machine Admin Agent

**Branch**: `001-standalone-machine-admin-agent` | **Date**: 2026-10-29 | **Spec**: specs/001-standalone-machine-admin-agent/spec.md

**Input**: Feature specification from `/specs/001-standalone-machine-admin-agent/spec.md`

## Summary

Build a standalone Python agent daemon (`apps/agent`) exposing a Pydantic AI admin agent with machine and app management tools, MCP, and skills. Register agents in the core API so web/mobile can discover and chat with multiple agents across machines. Provide install methods and a default local agent.

## Technical Context

**Language/Version**: Python 3.12 (agent + API), TypeScript/Next.js 16 (web), Dart/Flutter 3 (mobile)
**Primary Dependencies**: FastAPI, Pydantic AI, pydantic-ai-harness, SQLAlchemy, Alembic, uv
**Storage**: PostgreSQL (registry, sessions, audit), Redis (cache)
**Testing**: pytest (API/agent), vitest (web), flutter test (mobile)
**Target Platform**: Linux/macOS server daemon; web browser; mobile
**Performance Goals**: First token within 3s; 100 concurrent sessions per agent
**Constraints**: Approval required for destructive tools; least privilege; tenant isolation
**Scale/Scope**: Multi-tenant, multi-agent, multi-machine

## Constitution Check

Gates: extend existing monorepo; preserve conventions; security at server boundary; tests mandatory; incremental changes. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-standalone-machine-admin-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
apps/agent/                       # new standalone daemon
├── pyproject.toml
├── src/admin_template_agent/
│   ├── main.py
│   ├── agent/
│   ├── auth.py
│   ├── config.py
│   ├── mcp.py
│   ├── skills.py
│   └── session.py
├── tests/
├── Dockerfile
└── deploy/
apps/api/src/admin_template/modules/agents/   # registry
apps/web/app/agents/                          # UI
apps/mobile/lib/features/agents/               # mobile UI
```

**Structure Decision**: Add `apps/agent` as a new workspace app; extend `apps/api` with agents module; extend web/mobile with agent picker.

## Complexity Tracking

No violations.