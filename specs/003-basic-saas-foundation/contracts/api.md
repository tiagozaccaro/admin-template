# API Contract Changes (summary)

New/extended endpoints (under `/api/v1`):

- `POST /auth/register` — local registration
- `POST /auth/verify-email` — verify token
- `POST /auth/request-reset` — request password reset
- `POST /auth/reset-password` — reset with token
- `GET /users/me` — profile
- `PATCH /users/me` — update profile
- `DELETE /users/me` — soft-delete account
- `POST /tenants/{id}/invitations` — create invitation (expires 7d)
- `POST /invitations/{token}/accept` — accept
- `POST /invitations/{id}/revoke` — revoke
- `GET /health`, `/healthz`, `/readyz` — existing (verify)

All endpoints require tenant context where applicable; authorization enforced server-side. Errors follow existing consistent error format.