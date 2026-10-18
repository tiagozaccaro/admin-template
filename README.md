# Admin Template

A reusable monorepo admin template: Next.js web app, Flutter mobile app, FastAPI backend, and shared packages. Use it as the starting point for independent admin applications — bring your own domain logic, database schema, and integrations.

## Technology stack

| Area | Technology |
| --- | --- |
| Monorepo | pnpm workspaces + Turborepo |
| Web | Next.js 16 (App Router), React 19, TypeScript strict, Tailwind 4, shadcn/ui primitives |
| Mobile | Flutter 3.x / Dart |
| API | FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, uv |
| Shared | `@workspace/ui`, `@workspace/api-client`, `@workspace/eslint-config`, `@workspace/typescript-config` |
| Auth | OpenID Connect (Keycloak) foundations on web, mobile, and API |
| Dev tools | ESLint, Prettier, Ruff, Pyright, `dart analyze`, `flutter test`, pytest |

## Repository structure

```
admin-template/
├── apps/web           # Next.js admin web application
├── apps/mobile        # Flutter admin mobile application
├── apps/api           # FastAPI backend
├── packages/ui        # shared shadcn/ui primitives
├── packages/api-client# generated OpenAPI client placeholder
├── packages/eslint-config
├── packages/typescript-config
├── deploy/            # Docker Compose, Keycloak realm, Caddy
├── docs/              # architecture and development notes
└── AGENTS.md          # repository guidance for agents and contributors
```

## Prerequisites

- Node.js >= 20.9 and pnpm 11.25 (monorepo)
- Dart SDK 3.13+ and Flutter 3.x (mobile)
- Python 3.12+ and uv (API)
- Docker and Docker Compose (optional, for full local stack)

## Installation and setup

```bash
pnpm install
```

This installs web, API, and shared package dependencies via the pnpm workspace. For the mobile app:

```bash
cd apps/mobile && flutter pub get
```

For the API (Python dependencies via uv):

```bash
cd apps/api && uv sync
```

## Environment configuration

Copy the deploy environment example and adjust for local development:

```bash
cp deploy/.env.example deploy/.env
# edit deploy/.env with local values
```

Never commit real secrets. `deploy/.env` is gitignored; `deploy/.env.example` contains safe defaults.

The API resolves secrets from environment variables or Docker `_FILE` secret mounts; no secret values are stored in the repository.

## Starting the applications

### Web (Next.js)

```bash
pnpm --filter @admin-template/web dev
```

The web app runs on `http://localhost:3000`. It includes a generic dashboard, login, and signup pages. The login flow is a cookie-based development placeholder — replace it with your OIDC client integration before production use.

### API (FastAPI)

```bash
cd apps/api && uv run uvicorn admin_template.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API exposes `/health`, `/healthz`, and `/readyz`. Add your own routers under `apps/api/src/admin_template/api/v1/routers/`.

### Mobile (Flutter)

```bash
cd apps/mobile && flutter run
```

The mobile app targets the OIDC issuer configured via `ADMIN_TEMPLATE_OIDC_ISSUER` (defaults to `http://localhost:8080/realms/admin-template`).

### Full stack with Docker Compose

```bash
docker compose --env-file deploy/.env -f deploy/docker-compose.yml up -d --build
```

This starts PostgreSQL, Redis, Keycloak (importing the `admin-template` realm), the API, and the web app. Keycloak and Caddy are behind the `edge` network profile; start Caddy with `docker compose --profile edge up caddy`.

## Running tests and quality checks

### Monorepo (web + packages)

```bash
pnpm lint        # ESLint across workspaces
pnpm format      # Prettier
pnpm typecheck   # tsc --noEmit across workspaces
pnpm build       # turbo build
pnpm test        # turbo test
```

Run per workspace with `pnpm --filter <name> <task>`, e.g.
`pnpm --filter @admin-template/web build`.

### API (Python)

```bash
cd apps/api
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright
uv run pytest
```

Pytest contract tests exercise `/health`, `/healthz`, and `/readyz` without a database. Database-backed tests require a running PostgreSQL (see `deploy/.env.example`).

### Mobile (Flutter)

```bash
cd apps/mobile
flutter analyze
flutter test
```

## Building applications

- Web: `pnpm --filter @admin-template/web build` (standalone output for Docker)
- API: `cd apps/api && uv sync --frozen --no-dev` then build the Docker image in `deploy/docker-compose.yml`
- Mobile: `flutter build apk` or `flutter build ios` (host toolchain required)

## Docker and deployment

See `deploy/docker-compose.yml` and `deploy/.env.example`. Service images are built from `apps/api/Dockerfile` and `apps/web/Dockerfile`. The Compose project name is `admin-template`.

## How to add a new feature

1. Create a GitHub issue describing the feature and acceptance criteria.
2. Branch from `main`, implement, and open a pull request.
3. CI must pass: lint, format check, typecheck, tests, builds.
4. Squash merge into `main` after review and approval.

Shared changes (packages, CI, workflows) follow the same gated workflow.

## How to extend authentication, database access, and integrations

- Authentication: the API validates Keycloak JWTs (`apps/api/src/admin_template/core/security.py`); web and mobile include OIDC PKCE placeholders. Wire your issuer, audience, and client IDs via environment variables.
- Database: SQLAlchemy async session (`core/db.py`) with Alembic migrations in `apps/api/migrations/`. Add models under `apps/api/src/admin_template/modules/<context>/models/` and new migrations via `alembic revision --autogenerate`.
- Integrations: add API routers under `api/v1/routers/` and wire them in `api/main.py`. The `@workspace/api-client` package is a placeholder for a generated OpenAPI client.

## How to customize branding and application identity

- Project name: `admin-template` in `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `apps/api/pyproject.toml`, `deploy/docker-compose.yml`, and `deploy/.env.example`.
- Web title/theme: `apps/web/app/layout.tsx` plus `@workspace/ui/src/styles/globals.css` and `next-themes` (light/dark/system).
- Mobile title and theme: `apps/mobile/lib/main.dart` (`MaterialApp.title`, `ColorScheme.fromSeed`).
- Displayed bundle IDs: `android/app/build.gradle.kts` (`com.admin_template.mobile`) and iOS `Runner.xcodeproj/project.pbxproj`.
- Keycloak realm: `deploy/keycloak/realm-export.json` (realm `admin-template`) and `KEYCLOAK_ISSUER`/`KEYCLOAK_JWKS_URL` in `deploy/.env.example`.

Replace the placeholder logos, colors, and demo data (`apps/web/app/dashboard/data.json`) with your own.
