# Feature Parity Matrix

This document defines which capabilities are supported on both web and mobile to satisfy US3 (Switch platforms). Feature parity means: same supported capabilities, business rules, data operations, and authorization behavior, unless an approved platform limitation applies. Both clients must implement and verify equivalent functionality.

## Legend
- ✓ = Implemented / fully supported on platform
- WIP = Work in progress
- PL = Platform limitation (approved; rationale documented)
- N/A = Not applicable for this feature

## Core Features

| Feature | Web | Mobile | Notes / Rationale |
|---|---|---|---|
| User authentication (Google OIDC) | ✓ | ✓ | PKCE, CSRF protection, secure token/cookie handling (T030, T031) |
| Sign out / session revocation | ✓ | ✓ | Web: cookie revocation; Mobile: token revocation/refresh rotation |
| User profile display | ✓ | ✓ | `/me` endpoint consumed by both clients |
| Protected route handling | ✓ | ✓ | Redirect to login on unauthorized; authorized access enforced |
| Tenant list/switching | WIP | WIP | Implemented via T042/T043 per US4; parity maintained |
| Create tenant | WIP | WIP | Core tenant management (T042/T043) |
| Tenant membership management | WIP | WIP | Add/remove/change role (US4) |
| Invitations (create/accept/revoke) | WIP | WIP | In-app delivery default; email optional (US4) |
| Role-based access control | WIP | WIP | Enforced server-side; UI respects permissions (US5) |
| Dashboard (tenant-scoped metrics/activity) | WIP | WIP | Same aggregates from backend (US6) |
| Generic CRUD operations | WIP | WIP | Parity for core admin operations (US7/US10) |
| Notifications (in-app) | WIP | WIP | Tenant/user scoped (US8) |
| Audit history view | WIP | WIP | Read-only, tenant-scoped (US9) |
| Error handling & validation feedback | ✓ | WIP | Consistent error responses from API |

## Platform-specific Notes

| Platform | Details | Approved Limitation? |
|---|---|---|
| Web | Browser-based; supports httpOnly/SameSite/Secure cookies + CSRF double-submit | No - standard for web. |
| Mobile | Native; uses short-lived access token + refresh token in platform secure storage (Keychain/Keystore). No browser cookies for API auth. | Yes - platform security model requires token-based auth. Parity in capabilities and authz enforced server-side. |

## Verification Criteria

- [ ] Each feature marked WIP is tested end-to-end on both clients as part of its user story
- [ ] Negative tests (authz, invalid input, CSRF, etc.) behave identically in terms of rejection semantics
- [ ] Tenant isolation verified on both clients (cannot see cross-tenant data)
- [ ] Role restrictions verified on both clients per permission matrix
- [ ] Any deviation must be documented with explicit approved rationale

## Status Summary

- US1-2: Core auth/parity groundwork complete (auth flows implemented on both clients)
- US3 (this task): Parity matrix established; cross-platform smoke tests pending (T035)
- US4+: Remaining features tracked in parity matrix as implemented

