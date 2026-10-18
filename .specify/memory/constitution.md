<!-- Sync Impact Report
Version: 1.0.0 -> 1.1.0 (MINOR: twelve domain-specific principles replace the five general ones; Technology Stack and Tooling and Development Workflow and Quality Gates sections added)
Modified principles: I-V (Repository Understanding, Type Safety, Security, Testing and Evidence, Maintainability) replaced by I-XII
Added sections: Technology Stack and Tooling; Development Workflow and Quality Gates
Removed sections: none (prior Technology Stack, Development Workflow, Governance content folded into new sections)
Deferred items: none
-->

# Admin Template Constitution

## Core Principles

### I. Open-Source-First, Self-Hostable Architecture
All source code is open source. The platform must run entirely on self-hosted infrastructure operated by the organization, with no SaaS-only lock-in. Third-party services exist only as swappable adapters behind provider-neutral interfaces; no external service may become a hard dependency that prevents self-hosting.

### II. Modular Monolith
One deployable unit with internally isolated domain modules and explicit interfaces. Cross-module communication goes through published interfaces only; modules must not import implementation details of other modules. Shared UI, lint, and TypeScript configuration live in workspace packages (`@workspace/ui`, `@workspace/eslint-config`, `@workspace/typescript-config`).

### III. FastAPI as the Authoritative Business API
FastAPI is the single source of truth for business logic and state transitions. All clients (web, mobile, CLI) call the FastAPI API; no client may bypass it to mutate state directly. API boundaries use Pydantic validation and explicit Python types.

### IV. PostgreSQL as Source of Truth
PostgreSQL is the authoritative data store. Schema changes happen exclusively through versioned migrations; no ad-hoc DDL. Database tooling is read-only by default (`MCP_POSTGRES_URL`). Destructive database operations, force pushes, irreversible changes, privileged commands, and consequential external writes require approval before execution.

### V. Provider-Neutral AI and External-Source Adapters
AI providers and external data sources are accessed only through adapter abstractions. The core domain never imports provider-specific clients directly. Adapters are swappable, so no single provider can become a hard dependency or single point of failure.

### VI. Secure OIDC
Authentication is exclusively OpenID Connect (OIDC). No password-based authentication and no application-issued long-lived bearer tokens. OIDC follows secure defaults: short-lived tokens, PKCE for public clients, strict redirect-URI validation, and secrets never committed to the repository.

### VII. Multi-Tenant Authorization
Every request is scoped to a tenant. Tenant isolation is enforced at the API layer, not assumed in clients. Authorization is explicit and deny-by-default, least-privilege, and checked on every mutating and read path touching tenant data.

### VIII. Revisioned Content
All content is revisioned. Every create, update, or delete produces an immutable revision record with author, timestamp, and prior state. Content history is append-only and auditable; revisions cannot be silently overwritten or deleted.

### IX. Tested Cross-Device Sync
Web and mobile clients synchronize state across devices. Sync behavior (conflict resolution, offline queueing, retry) is covered by automated tests on both platforms and verified on real device pairs, not emulators alone.

### X. Accessible Web and Mobile UX
Web UX meets WCAG 2.1 AA: keyboard navigation, focus management, ARIA labels, sufficient color contrast, and reduced-motion support. Flutter mobile UX uses semantics labels and scalable text. Accessibility is verified in CI, not assumed.

### XI. Comprehensive Automated Tests
API: pytest unit and integration tests with coverage thresholds. Web: tests under the repo's TS tooling (ESLint/typecheck plus Playwright where configured). Mobile: `flutter_test`. Tests run on every PR and must pass before merge. Never claim checks passed unless executed.

### XII. Production-Grade Observability
All services expose structured logging, metrics, distributed tracing context, and health endpoints. Logs carry diagnostic context and never secrets. Alerts fire on downtime, sync failures, and authentication anomalies.

## Technology Stack and Tooling

- API: Python 3.12+, FastAPI, Pydantic, uv, PostgreSQL; schema migrations via Alembic (or equivalent versioned migration tool).
- Web: Next.js 16, React 19, TypeScript strict mode, ESLint, Prettier, Turbo, pnpm.
- Mobile: Flutter 3.x / Dart; `flutter_test`, `flutter analyze`, `flutter format`.
- Typing: strict TypeScript with no explicit `any`; explicit Python types; Pyright for Python typechecking.
- Lint/format/test: Ruff (lint + format), Pyright, pytest; ESLint + `tsc --noEmit`; `dart analyze` + `flutter test`.
- Secrets: never committed; `.env.mcp.local` is gitignored; MCP and runtime values use `{env:VAR}` references.

## Development Workflow and Quality Gates

Every feature or behavior change must follow, in order:

1. GitHub issue describing the feature and its acceptance criteria.
2. Feature branch created from protected `main`.
3. Pull request with review and approval before merge.
4. CI passes: lint, format check, typecheck (TypeScript and Pyright), tests (pytest, Flutter, web test tooling), and build.
5. Squash merge to `main` only. `main` is protected: required reviews, required status checks, no direct pushes.

Changes to shared packages, CI configuration, workflows, or the Constitution itself follow the same gated workflow.

## Governance

This Constitution supersedes all other development practices in the repository (including `AGENTS.md`) where they conflict. Amendments must be documented in a pull request against `.specify/memory/constitution.md` with a recorded rationale and a semantic version bump: MAJOR for backward-incompatible principle removals or redefinitions, MINOR for new or materially expanded principles, PATCH for clarifications and wording. Every PR is checked for Constitution compliance; complexity and exemptions must be justified and recorded.

**Version**: 1.1.0 | **Ratified**: 2026-10-16 | **Last Amended**: 2026-10-16
