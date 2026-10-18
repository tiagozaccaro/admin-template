---
name: postgres-migrations
description: Secure PostgreSQL migration and query practices for admin-template. Use when adding database changes, SQL migrations, read/write paths, indexes, or validating database access via the Postgres MCP.
---

# PostgreSQL Migrations

## Constraints
- Postgres MCP defaults to read-only access. Treat writes as consequential and require explicit approval.
- Never hardcode connection URLs; use env-configured URLs.
- Follow least privilege: separate migration credentials from runtime credentials.

## Rules
- Migrations are additive and reversible when feasible. Prefer create over drop/rewrite.
- Never run destructive operations without explicit approval.
- Add constraints/indexes with concurrency safety (avoid locking heavy tables in production).
- Keep migration files deterministic and reviewed.
- Validate schema changes with read-only MCP queries first.
- Prevent SQL injection: parameterized queries only.
- Ensure migration checks pass before considering work complete.
