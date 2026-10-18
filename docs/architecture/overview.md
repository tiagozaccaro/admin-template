# Admin Template Architecture

## Applications

- `apps/web`: Next.js 16 web app (App Router, React 19, shadcn/ui primitives)
- `apps/mobile`: Flutter mobile app
- `apps/api`: FastAPI backend

## Shared packages

- `packages/ui`: shared UI primitives and layout components
- `packages/api-client`: generated OpenAPI client placeholder
- `packages/eslint-config`, `packages/typescript-config`: shared TS tooling config

## Boundaries

- The FastAPI API is the authoritative backend. Clients call the API; clients do not mutate state directly.
- The web app owns session/UI routing under `apps/web/app` (dashboard, login, signup).
- The mobile app owns its shell and navigation under `apps/mobile/lib`.
- Shared UI code lives only in `packages/ui`; app-specific pages stay in their apps.

## Extension points

- API: add routers under `apps/api/src/admin_template/api/v1/routers/`, register them in `apps/api/src/admin_template/api/main.py`.
- DB: models under `apps/api/src/admin_template/modules/<context>/models/`; Alembic migrations under `apps/api/migrations/alembic/versions/`.
- Auth: OIDC/JWT validation in `apps/api/src/admin_template/core/security.py`; issuer/audience via environment variables.
- Web: routes under `apps/web/app`; UI primitives from `@workspace/ui`.
- Mobile: screens and features under `apps/mobile/lib/features/` and `apps/mobile/lib/auth/`.

## Deployment

Local full stack: `deploy/docker-compose.yml` (PostgreSQL, Redis, Keycloak, API, web; Caddy behind the `edge` profile). Environment defaults in `deploy/.env.example`.
