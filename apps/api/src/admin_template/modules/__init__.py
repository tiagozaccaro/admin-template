"""Admin Template API bounded-context modules.

Each subpackage exposes a public ``__init__.py`` interface. Cross-module
communication goes through published interfaces only; modules must not import
implementation details of other modules.

Bounded contexts:

- identity: authenticated users (OIDC keycloak_sub keyed)
- workspace: workspaces, memberships, and roles (owner/member/viewer)

Extension point: add new bounded contexts under
``apps/api/src/admin_template/modules/<context>/`` and expose routers under
``apps/api/src/admin_template/api/v1/routers/``.
"""

__all__ = []
