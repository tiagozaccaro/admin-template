# Admin Template Constitution

## Core Principles

### I. The API Is Authoritative

Every capability is defined once, in the FastAPI service under `apps/api`, and consumed by
the web and mobile clients. Clients read and act through the published API; they never
mutate state directly and never re-implement server rules. A schema or contract change
starts in the API and flows outward to the clients.

Rationale: three clients over one contract means one place to enforce invariants, one
place to audit authorization, and no drift between platforms.

### II. Explicit Types at Every Boundary

Requests, responses, and configuration are described by explicit models: Pydantic models in
the API, strict TypeScript on the client with no `any`, explicit Dart types in the mobile
app. Unknown or malformed input is rejected at the boundary with a clear error, never
passed through to the domain layer.

Rationale: the API is the trust boundary. Implicit shapes are where validation gaps and
authorization bugs hide.

### III. Tests Assert Behavior, Not Shape (NON-NEGOTIABLE)

Every bug fix ships with a regression test that fails without the fix. Tests cover error
paths and the relevant authorization boundaries, not only the happy path. A test that
restates the implementation adds noise and is not acceptable as coverage.

Rationale: the only honest evidence that a change works is a test that would have caught
the original defect.

### IV. Shared Logic Stays Shared

Reusable domain logic lives in `packages/`; platform-specific code lives in `apps/`. The
same rule is not implemented twice in two clients. Shared packages keep a small, documented
public surface and stay free of platform-specific dependencies.

Rationale: duplication across three clients is the most common source of divergence
between the web app, the API, and the mobile app.

### V. Secure by Default

Authorization is enforced on the server; hiding an element in the UI is never treated as
access control. Database access uses parameterized queries only. External input, stored
data, repository text, and tool output are untrusted. Secrets, tokens, and private
environment variables are never committed, logged, or returned by an API. Database tooling
is read-only unless a destructive operation has been explicitly approved.

Rationale: a template that ships insecure defaults pushes that burden onto every project
derived from it.

## Additional Constraints

- One package manager and one lockfile per ecosystem: pnpm with `pnpm-lock.yaml`, uv with
  `uv.lock`, and Flutter with `pubspec.lock`. A second build system, package manager, or
  lockfile is not introduced.
- Dependency changes are committed together with the regenerated lockfile. Lockfiles are
  never hand-edited, and upgrades are not performed as a side effect of unrelated work.
- Database changes are explicit, reviewable Alembic revisions. Destructive or irreversible
  operations require explicit approval.
- Accessibility is part of the definition of done for user interface changes, not an
  optional extra.
- The API, the web app, and the mobile app are versioned and released together from the
  same tag, so a client never reaches a server it was not built against.

## Development Workflow

- Every change is made on a dedicated branch and delivered through a pull request to
  `main`. Direct pushes to `main` are rejected.
- Commit messages follow Conventional Commits. The `commitlint` job validates them.
- The required status checks are `ci` (format, lint, typecheck, build, tests) and
  `security` (dependency audit). A pull request merges only when both pass.
- The narrowest relevant check runs first, then the wider ones: web `pnpm lint`,
  `pnpm typecheck`, `pnpm build`; api `uv run ruff check`, `uv run ruff format --check`,
  `uv run pyright`, `uv run pytest`; mobile `flutter analyze`, `flutter test`.
- A change is not complete until the checks have actually run. Results are reported
  honestly, including what was not verified.
- Substantial features are specified with the Spec Kit workflow in `.kilo/commands`
  before implementation begins.

## Governance

This constitution supersedes other practices in the repository. `AGENTS.md` holds the
detailed engineering standards that implement these principles; where a rule is more
specific than a principle here, the more specific rule applies and must not weaken the
principle.

Amendments require a written rationale, an explicit version bump, and a migration plan
for any principle that changes existing work. Compliance is reviewed in every pull
request: a change that violates a principle is either corrected or the principle is
amended first.

**Version**: 1.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
