# Implementation Plan: Admin Template Product

**Branch**: `002-admin-template-product` | **Date**: 2026-10-18 | **Spec**: `/specs/002-admin-template-product/spec.md`

**Input**: Feature specification from `/specs/002-admin-template-product/spec.md`

## Summary

Build a reusable, production-oriented multi-platform admin foundation: Flutter mobile + Next.js/shadcn web + Python FastAPI backend, with Google OIDC, multi-tenant organizations and roles, dashboard, generic CRUD, notifications, and audit history. Resolve the nine open decisions with documented rationale, then execute in the phased delivery plan (Phase 0–7). All work MUST preserve feature parity, server-side authorization, and tenant isolation.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x strict (web), Dart 3.x (mobile)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, authlib, uv; Next.js 16, React 19, shadcn/ui, Tailwind 4, TanStack Query, pnpm, Turborepo; Flutter 3.x, Riverpod
**Storage**: PostgreSQL 15+ (default relational), Alembic migrations
**Testing**: pytest (backend), Vitest/Playwright (web), flutter test (mobile)
**Target Platform**: Linux containers (backend), modern browsers (web), iOS 15+ & Android 8+ (mobile)
**Project Type**: multi-app monorepo (web + mobile + api)
**Performance Goals**: paginated list endpoints; tenant-scoped dashboard queries; AI streaming partial responses
**Constraints**: <200ms p95 for simple reads; no unbounded dataset loads; optional integration failures must not crash unrelated features
**Scale/Scope**: template foundation; 10k users/tenant-scale targets deferred to measurement

## Constitution Check

- Article I (Tech standards): Flutter/Dart mobile, Next.js/TS web, shadcn/ui, Python/FastAPI, PostgreSQL, SQLAlchemy 2.x + Alembic + Pydantic, uv, strict TS + pnpm — all satisfied.
- Article II (Parity): parity matrix maintained; same capabilities/authorization — satisfied by design.
- Article III (Architecture/modularity): modular monolith, separated layers — satisfied.
- Article IV (UI systems): shadcn/ui web, reusable Flutter widgets, light/dark — satisfied.
- Article V (Auth): Google OIDC first, distinct internal/external identities, server-side secrets — satisfied.
- Article VI (Security): server-side authz/tenant scope, CSRF, no secrets in logs — satisfied.
- Article VII (Multi-tenancy): explicit membership, Owner/Admin/Member/Viewer, fail-closed cross-tenant — satisfied.
- Article VIII (Testing): backend/web/mobile tests, negative security tests — satisfied.
- Article IX (Accessibility): keyboard nav, visible focus, touch targets, color not sole status — satisfied.
- Article X (Observability): structured logs, correlation ids, health/readiness — satisfied.
- Article XI (Documentation/genericity): setup, config, migrations, testing, deployment, extension docs — satisfied.
- Article XII (Spec-driven): Spec Kit workflow — satisfied.
- Article XIII (PR governance): branches/PRs, focused review — satisfied.
- Article XIV (Dependencies): review for security/maintenance/license — satisfied.

Gates pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/002-admin-template-product/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── web/                # Next.js + shadcn/ui
├── mobile/             # Flutter
└── api/                # FastAPI
packages/
├── web-ui/             # Shared web components
├── web-config/         # Shared web tooling/config
└── api-client-ts/      # Generated TypeScript client
mobile/packages/
└── admin_ui/           # Reusable Flutter widgets/theme
backend/src/admin_template/
├── api/
├── core/
├── modules/
├── auth/
├── permissions/
├── tenancy/
├── database/
├── jobs/
└── observability/
packages/contracts/     # OpenAPI generation/source tooling
migrations/
infrastructure/
tests/integration, contract, e2e
specs/
docs/
```

**Structure Decision**: Monorepo with apps/{web,mobile,api}, shared packages, and backend/src/admin_template modular monolith. Migrations under migrations/ (Alembic). Contracts generated from FastAPI OpenAPI into packages/api-client-ts and mobile client. Worker directory only introduced when an actual processing need arises (not in first release).

## Open Decisions — Resolved

1. **Mobile OS/targets**: iOS 15+ and Android 8+ (API 26+). Flutter stable channel. Rationale: broad coverage; Flutter supports both with one codebase. Rejected: single-platform (limits template value).
2. **Session architecture**: Web uses backend-issued httpOnly, SameSite, Secure cookie with CSRF token (double-submit) for state-changing requests; mobile uses short-lived access token + refresh token in platform secure storage (Keychain/Keystore). Rationale: matches platform security models. Rejected: shared browser session on mobile (insecure).
3. **OIDC implementation**: authlib (maintained, supports OIDC discovery, PKCE, nonce) on FastAPI. Rationale: maintained, well-tested. Rejected: hand-rolled JWT validation (error-prone).
4. **State management/cache**: Riverpod (mobile), TanStack Query (web). Rationale: mature, testable, cache invalidation. Rejected: ad-hoc state (divergence risk).
5. **Invitation delivery**: pluggable delivery adapter; default in-app notification + optional email adapter (SMTP/provider). If no email adapter configured, report honestly that delivery did not occur. Rationale: honest status; extensible. Rejected: pretending delivery.
6. **Deployment target**: containerized (Docker) backend + web; documented production reference (container platform of choice). Secrets via environment/secret manager. Rationale: portable. Rejected: platform-locked deployment.
7. **Worker in first release**: No separate worker initially; background work runs in-process or via scheduled tasks where trivial; introduce worker when a real processing need (email queue) emerges. Rationale: avoid empty scaffolding.
8. **Workspace layout/API client generation**: pnpm workspaces + Turborepo; OpenAPI generated from FastAPI; TypeScript client via openapi-typescript + openapi-fetch; Dart client via openapi-generator (or hand-typed DTOs if generator quality insufficient), documented. Rationale: reproducible contracts.

## Complexity Tracking

No constitution violations requiring justification. Complexity is inherent to multi-platform foundation but justified by product scope.
