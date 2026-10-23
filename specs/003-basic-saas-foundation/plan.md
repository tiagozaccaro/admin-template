# Implementation Plan: Complete the Basic SaaS Foundation

**Branch**: `003-basic-saas-foundation` | **Date**: 2026-10-23 | **Spec**: `specs/003-basic-saas-foundation/spec.md`

**Input**: Feature specification from `/specs/003-basic-saas-foundation/spec.md`

## Summary

Complete the basic SaaS foundation by implementing missing/incomplete capabilities: local auth lifecycle, tenant isolation hardening, invitation lifecycle, RBAC enforcement, profile/settings, email abstraction, audit, minimal ops, and tests. Preserve existing stack (Next.js 16, FastAPI, Flutter) and modules.

## Technical Context

**Language/Version**: Python 3.12 (API), TypeScript/Next.js 16 (web), Dart/Flutter 3 (mobile)
**Primary Dependencies**: FastAPI, SQLAlchemy 2, Alembic, Pydantic 2, Next.js, shadcn/ui, Keycloak OIDC
**Storage**: PostgreSQL (via SQLAlchemy/Alembic)
**Testing**: pytest (API), pnpm lint/typecheck/test (web), flutter test (mobile)
**Target Platform**: Linux server (API), web browsers, mobile (iOS/Android)
**Project Type**: Web application + API + mobile app
**Performance Goals**: Standard web app responsiveness (<2s page loads)
**Constraints**: No new frameworks; reuse existing abstractions; optional features decoupled
**Scale/Scope**: Starter template; small-to-medium SaaS workloads

## Constitution Check

Gates derived from constitution:
- Preserve existing stack/architecture: PASS (incremental changes only)
- Evidence-based decisions: PASS (spec grounded in repo)
- Incremental/reversible: PASS (batches defined)
- Security/tenant isolation: PASS with work required (P0 batches)
- Testing/quality: PASS with work required (tests in batches)
- No new frameworks without justification: PASS (email abstraction uses existing)

## Project Structure

### Documentation (this feature)

```text
specs/003-basic-saas-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
apps/api/src/admin_template/
├── auth/
├── core/
├── modules/
│   ├── identity/
│   ├── tenancy/
│   ├── permissions/
│   ├── notifications/
│   └── audit/ (new)
apps/web/app/
packages/ui/
```

**Structure Decision**: Reuse existing monorepo layout; add audit module and email abstraction within existing modules; no new top-level projects.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Local auth alongside OIDC | Starter usability without Keycloak | OIDC-only blocks local dev/testing |
| Soft-delete users | Audit retention + compliance | Hard delete breaks audit integrity |