# Research: Admin Template Product

## Decision: Mobile OS and targets
- **Decision**: iOS 15+ and Android 8+ (API 26+), Flutter stable.
- **Rationale**: Broad coverage with one codebase; Flutter supports both well.
- **Alternatives considered**: iOS-only (limits template value); Android-only (same).

## Decision: Session architecture
- **Decision**: Web: backend-issued httpOnly/SameSite/Secure cookie + CSRF double-submit token. Mobile: short-lived access token + refresh token in platform secure storage.
- **Rationale**: Matches platform security models; avoids assuming browser sessions on native.
- **Alternatives considered**: shared browser session on mobile (insecure); long-lived tokens (risk).

## Decision: OIDC implementation
- **Decision**: authlib on FastAPI.
- **Rationale**: Maintained, supports OIDC discovery, PKCE, nonce, signature validation.
- **Alternatives considered**: hand-rolled JWT validation (error-prone); other libraries (less maintained).

## Decision: State management and API cache
- **Decision**: Riverpod (mobile), TanStack Query (web).
- **Rationale**: Mature, testable, cache invalidation, parity of semantics.
- **Alternatives considered**: ad-hoc state (divergence risk); Redux (heavier).

## Decision: Invitation delivery
- **Decision**: Pluggable delivery adapter; default in-app notification + optional email adapter. Report honestly if delivery unavailable.
- **Rationale**: Honest status; extensible channels.
- **Alternatives considered**: claiming delivery when not (rejected).

## Decision: Deployment target
- **Decision**: Containerized (Docker) backend + web; documented production reference; secrets via env/secret manager.
- **Rationale**: Portable across platforms.
- **Alternatives considered**: platform-locked (rejected).

## Decision: Worker in first release
- **Decision**: No separate worker initially; introduce when a real processing need emerges.
- **Rationale**: Avoids empty scaffolding.
- **Alternatives considered**: always-on worker (unnecessary complexity).

## Decision: Workspace layout and client generation
- **Decision**: pnpm workspaces + Turborepo; OpenAPI from FastAPI; TS client via openapi-typescript + openapi-fetch; Dart client via openapi-generator (fallback hand-typed DTOs).
- **Rationale**: Reproducible contracts; documented generation.
- **Alternatives considered**: manual clients (drift risk).

## Decision: Database access and migrations
- **Decision**: SQLAlchemy 2.x async, Alembic, PostgreSQL 15+.
- **Rationale**: Mature, typed, migration support.
- **Alternatives considered**: other ORMs (less ecosystem).

## Decision: Auth library for sessions
- **Decision**: Server-side sessions stored in DB (or signed cookies) with revocation support; mobile tokens revocable via refresh token rotation.
- **Rationale**: Enables logout/revocation semantics.
- **Alternatives considered**: stateless-only JWT (hard revocation).
