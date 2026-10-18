---
name: fastapi-engineering
description: FastAPI + Python + Pydantic development for admin-template API. Use when implementing routes, schemas, services, HTTP clients, configuration, tests, or async flows in apps/api.
---

# FastAPI Engineering

## Stack
- Python >=3.12, FastAPI, Pydantic v2, pydantic-settings, HTTPX.
- uv workspace, Ruff, Pyright, pytest/pytest-cov.
- Entry point api.main:app; package source in apps/api/src/api.

## Rules
- Define explicit Pydantic request/response models for every endpoint; never return raw ORM/domain objects.
- Validate settings through pydantic-settings; load secrets from env, never hardcode.
- Use async endpoints for network/database IO; HTTPX async client with explicit timeouts.
- Keep route handlers thin; move logic into services/modules.
- Explicit type hints everywhere; Pyright strict should pass.
- Handle errors intentionally; don't expose internal error details.
- Tests cover happy + error paths; HTTP clients mock external dependencies.
- Run `uv run ruff check src tests`, `uv run ruff format`, `uv run pyright`, `uv run pytest`, and `uv lock --check`.
