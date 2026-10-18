# Admin Template Architecture

## Applications
- apps/web: Next.js 16 web app (shadcn/ui)
- apps/mobile: Flutter mobile app
- apps/api: FastAPI backend

## Shared packages
- packages/ui: shared UI primitives
- packages/api-client: generated OpenAPI client
- packages/eslint-config, packages/typescript-config

## Extension points
- API: add routers under apps/api/src/admin_template/api/v1/routers
- DB: models under apps/api/src/admin_template/modules/<context>/models
- Web: routes under apps/web/app
