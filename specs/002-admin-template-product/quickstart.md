# Quickstart: Admin Template Validation

## Prerequisites
- Node.js, pnpm, Python 3.11+, uv, Flutter stable, PostgreSQL 15+, Docker (optional).

## Setup
1. Install dependencies: `pnpm install` (web), `uv sync` (api), `flutter pub get` (mobile).
2. Configure env from `.env.example` files (no real secrets).
3. Start PostgreSQL; apply migrations: `uv run alembic upgrade head`.
4. Start API: `uv run uvicorn admin_template.main:app --reload`.
5. Start web: `pnpm --filter web dev`.
6. Run mobile: `flutter run` on a supported target.

## Validation scenarios
- Health endpoint returns 200.
- Google login works on web and mobile; logout revokes access.
- Tenant switch shows only authorized records; cross-tenant tampering fails.
- Dashboard metrics reflect real data and update on tenant switch.
- CRUD workflow (list/search/filter/create/edit/delete) works on both clients with validation.
- AI conversation persists and streams; provider failure shows AI-unavailable state without breaking dashboard.
- Unauthorized API calls return 401/403; negative security tests pass.
- Lint/typecheck/test commands pass for all stacks.
