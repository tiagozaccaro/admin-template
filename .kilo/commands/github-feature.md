---
description: Implement a GitHub-tracked feature end-to-end: branch, code, tests, commit, push, and open a linked pull request. Never merge without explicit authorization.
---

## User Input

```text
$ARGUMENTS
```

## Pre-Execution Checks

1. Run `/github-task` first (or confirm the Issue, branch, and acceptance criteria are already established).
2. Confirm the working tree is clean or that existing user changes are preserved.
3. Confirm the current branch is not `main`.
4. Fetch the latest remote state: `git fetch origin`.

## Outline

1. **Start from a GitHub Issue**
   - Identify the Issue number and short description from the task input.
   - Confirm the Issue has acceptance criteria and verification steps.
2. **Create the appropriate feature branch**
   - Predictable name: `feature/<NUMBER>-short-description` (or `fix/`, `refactor/`, `ci/`, `docs/`).
   - Base the branch on the current target branch (`main`).
   - If the working tree has unrelated user work, preserve it on a safe branch first.
3. **Implement incrementally**
   - Follow the Issue's acceptance criteria.
   - Use the Spec Kit workflow (`/speckit.*`) for substantial features when available.
   - Run the narrowest relevant checks after each change (format, lint, typecheck, tests).
4. **Run relevant tests and inspect the diff**
   - Frontend: `pnpm format`, `pnpm lint`, `pnpm typecheck`, `pnpm build` (web), `pnpm test` (if configured).
   - Backend: `uv run ruff check`, `uv run ruff format --check`, `uv run pyright`, `uv run pytest`.
   - Mobile: `dart format --output=none --set-exit-if-changed .`, `flutter analyze`, `flutter test`.
   - Review the diff for correctness, security, unintended changes, and missing tests.
5. **Commit and push the branch**
   - Commit logical, reviewable units.
   - Use Conventional Commits: `<type>(<scope>): <subject>`. Allowed types are `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`; allowed scopes are `web`, `api`, `mobile`, `ui`, `api-client`, `ci`, `deps`, `docs`. The header is limited to 100 characters and the `commitlint` CI job rejects anything else.
   - Never commit secrets, credentials, or generated local configuration.
   - Push the branch: `git push -u origin <branch>`.
6. **Open a pull request targeting `main`**
   - Link the relevant Issue and include `Closes #ISSUE_NUMBER` when appropriate.
   - Include a summary, implementation details, testing evidence, risks, and migration/deployment notes.
7. **Report CI status and remaining review requirements**
   - Wait for required CI checks to finish successfully.
   - Resolve review comments and failing checks.
   - **Never merge unless explicitly authorized and permitted by policy.**

## Done When

- [ ] Implementation complete on a dedicated branch.
- [ ] Relevant tests and quality checks pass locally.
- [ ] Diff reviewed for correctness, security, and missing tests.
- [ ] Branch pushed and a linked PR exists targeting `main`.
- [ ] CI checks reported; review requirements communicated.
- [ ] Merge status explicitly reported (merged vs. awaiting review).