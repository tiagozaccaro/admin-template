---
description: Start a GitHub-tracked task: inspect repo/Git, find or create an Issue, define acceptance criteria, map parent/child Issues, confirm branch and task plan before implementation.
---

## User Input

```text
$ARGUMENTS
```

## Pre-Execution Checks

1. Confirm the working tree is clean or that existing user changes are preserved.
2. Confirm the current branch is not `main` (never develop directly on main).
3. Confirm GitHub CLI authentication (`gh auth status`) and repository access.

## Outline

1. **Inspect repository and Git status**
   - Run `git status`, `git branch -a`, `git remote -v`, `git log --oneline -5`.
   - Identify the default branch (`main`), existing Issues, Projects, and branch protections.
2. **Find or create the GitHub Issue**
   - Search existing Issues first: `gh issue list --search "$ARGUMENTS"`.
   - If none match, create one with a clear objective, scope, acceptance criteria, and verification steps.
   - Use labels from the repository convention: `feature`, `bug`, `maintenance`, `security`, `documentation`, `ci-cd`, `testing`.
   - For larger features, create a parent Issue first, then smaller actionable child Issues.
3. **Define acceptance criteria and testing requirements**
   - Write explicit, verifiable acceptance criteria in the Issue body.
   - Map each criterion to a concrete verification step (command, test, or manual check).
4. **Map larger work to parent and child Issues**
   - Parent Issue: the overall feature/change.
   - Child Issues: independently deliverable tasks (e.g., `feature/123-auth`, `fix/124-login`).
5. **Confirm the branch and task plan**
   - Predictable branch name: `feature/<NUMBER>-short-description`, `fix/<NUMBER>-...`, `refactor/<NUMBER>-...`, `ci/<NUMBER>-...`, `docs/<NUMBER>-...`.
   - Confirm the plan with the user before implementation begins.

## Done When

- [ ] Repository and Git state inspected and reported.
- [ ] GitHub Issue exists (reused or created) with acceptance criteria and verification steps.
- [ ] Parent/child Issue mapping defined for large work.
- [ ] Branch name and task plan confirmed before implementation.