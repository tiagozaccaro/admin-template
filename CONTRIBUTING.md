# Contributing

## Branch policy

`main` is protected. Direct pushes are rejected, including by administrators.

| Rule | Value |
| --- | --- |
| Merges | Pull request only |
| Required status checks | `ci`, `security` |
| Required approvals | 0, so a single maintainer can merge their own pull request |
| Force pushes | Blocked |
| Branch deletion | Blocked |
| Stale approvals | Dismissed on new commits |

Feature branches are short lived and are deleted after the pull request is merged.

### Branch naming

| Prefix | Use |
| --- | --- |
| `feature/<NUMBER>-<slug>` | New user visible capability, e.g. `feature/042-tenant-invite` |
| `fix/<NUMBER>-<slug>` | Bug fix, e.g. `fix/051-dashboard-total` |
| `refactor/<NUMBER>-<slug>` | Behaviour preserving change, e.g. `refactor/053-crud-base` |
| `ci/<NUMBER>-<slug>` | Pipelines and tooling, e.g. `ci/060-release-workflow` |
| `docs/<NUMBER>-<slug>` | Documentation only, e.g. `docs/061-branch-policy` |

`<NUMBER>` is the GitHub Issue the work belongs to. Keep the slug short and descriptive.

### Merging

Prefer squash merge so the history on `main` stays linear and one commit maps to one
change. The branch is deleted once the pull request is merged.

GitHub does not let an author approve their own pull request, so no approving review is
required. The `ci` and `security` checks plus the conversation resolution rule are what
gate a merge. CODEOWNERS are still notified when `apps/api`, `packages/ui` or
`packages/api-client` change.

## Commit messages

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) and are
validated by `commitlint` in CI.

```
<type>(<optional scope>): <subject>
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`,
`chore`, `revert`.

Allowed scopes: `web`, `api`, `mobile`, `ui`, `api-client`, `ci`, `deps`, `docs`.

Examples:

```
feat(api): add tenant invite endpoint
fix(web): keep the dashboard total in sync
ci: run the dependency audit on every pull request
```

The header is limited to 100 characters. Merge and revert commits are exempt.

Because `main` is merged with squash, the pull request title becomes the commit message on
`main`. The title must therefore follow the same format, and the body of the pull request
becomes the commit body.

## Local validation

Run the same checks CI runs before opening a pull request:

```sh
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm --filter @admin-template/web build
```

```sh
cd apps/api && uv sync --frozen && uv run ruff format --check src tests \
  && uv run ruff check src tests && uv run pyright && uv run pytest
```

```sh
cd apps/mobile && flutter analyze && flutter test
```

Commit messages can be checked locally with commitlint:

```sh
pnpm lint:commit
```

Dependency vulnerabilities are checked with:

```sh
pnpm audit --audit-level=high
cd apps/api && uv export --frozen --no-dev --no-hashes --no-emit-project \
  --format requirements-txt -o requirements.txt && uvx pip-audit -r requirements.txt
```

## Pull requests

1. Branch off `main` following the naming rules above.
2. Keep the pull request focused; one logical change per pull request.
3. Make sure CI is green: `ci` (lint, typecheck, build, tests) and `security` (dependency
   audit) must pass.
4. Request a review from the code owners listed in `.github/CODEOWNERS`.
5. Merge with squash and delete the branch.

For substantial features, use the Spec Kit workflow in `.kilo/commands/speckit.*` to
produce the specification, plan, and task list before implementing.

## Releases

Releases are cut from `main` by pushing a semantic version tag:

```sh
git tag v0.1.0
git push origin v0.1.0
```

The `release` workflow then:

1. Builds the web bundle and packages it as `web-<tag>.tar.gz`.
2. Builds and pushes the `web` and `api` container images to `ghcr.io`.
3. Attaches the artifacts to a GitHub release with generated release notes.

Tags containing a `-` are published as pre-releases. The `release` GitHub environment
holds the deployment secrets and should be restricted to version tags. A release can also
be started manually from the Actions tab with a `workflow_dispatch` input.

## Code owners

`apps/api`, `packages/ui` and `packages/api-client` hold the shared logic used by every
platform, so changes there need a code owner review. `.github` and `deploy` cover the
release tooling and the deployment configuration.
