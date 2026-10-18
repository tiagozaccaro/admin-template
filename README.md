# Admin Template

A reusable monorepo admin template: Next.js web app, Flutter mobile app, FastAPI backend, shared packages.

## Structure

- `apps/web` — Next.js web application
- `apps/mobile` — Flutter mobile application
- `apps/api` — FastAPI backend
- `packages/*` — shared packages

## Setup

```bash
pnpm install
```

### Web

```bash
pnpm --filter @admin-template/web dev
```

### API

```bash
cd apps/api && uv sync && uv run uvicorn admin_template.api.main:app --reload
```

### Mobile

```bash
cd apps/mobile && flutter pub get && flutter run
```
