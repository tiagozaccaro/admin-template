"""Admin Template API bounded-context modules.

Each subpackage exposes a public ``__init__.py`` interface. Cross-module
communication goes through published interfaces only; modules must not import
implementation details of other modules (constitution II).

Bounded contexts:

- identity: users, accounts, integrations
- workspace: workspaces, memberships, roles
- sources: source registration, ingestion adapters
- stories: discovery, comparison
- evidence: evidence collection
- ai: provider config, gateway adapter, PydanticAI workflows
- content: ideas, scripts, drafts, revisions
- projects: project organization
- jobs: Dramatiq actors, outbox publisher
- sync: revisioned sync endpoints
"""

__all__ = []
