# Quickstart Validation

1. Apply Alembic migrations; verify new columns/tables.
2. Start API and web; register a local user; verify email (check logs for no-op provider token); reset password.
3. Create tenant; invite user; accept invitation; verify expiration/revocation.
4. Run cross-tenant isolation tests and RBAC negative tests.
5. Run `pnpm lint`, `pnpm typecheck`, `pnpm test`, `uv run pytest`, `flutter analyze`.