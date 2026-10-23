---
description: Fix a GitHub-tracked bug: reproduce, create a dedicated fix branch, add a regression test, implement the smallest safe fix, and open a linked PR.
---

## User Input

```text
$ARGUMENTS
```

## Pre-Execution Checks

1. Confirm GitHub CLI authentication (`gh auth status`) and repository access.
2. Confirm the working tree is clean or that existing user changes are preserved.
3. Confirm the current branch is not `main`.

## Outline

1. **Start from an Issue or create one**
   - Search existing Issues first: `gh issue list --search "$ARGUMENTS"`.
   - If none match, create one with a clear bug report: symptoms, reproduction steps, expected behavior, actual behavior, and environment.
   - Label it `bug`.
2. **Reproduce the bug and record expected behavior**
   - Document the exact reproduction steps and the expected vs. actual outcome.
   - Capture evidence (logs, screenshots, test output) without exposing secrets.
3. **Create a dedicated fix branch**
   - Predictable name: `fix/<NUMBER>-short-description`.
   - Base the branch on the current target branch (`main`).
4. **Add a regression test where appropriate**
   - Write a focused test that fails before the fix and passes after.
   - Use the repository's existing test framework (pytest, flutter test, or vitest/jest if configured).
5. **Implement the smallest safe fix**
   - Make the minimal change that resolves the Issue without bypassing security controls.
   - Follow existing code conventions and style.
6. **Run tests, create the PR, and track the result**
   - Run the narrowest relevant checks (format, lint, typecheck, tests).
   - Commit with a Conventional Commits message: `fix(<scope>): <subject>`. The `commitlint` CI job rejects any other format.
   - Push the branch.
   - Open a PR targeting `main` with `Closes #ISSUE_NUMBER`.
   - Report CI status and review requirements.
   - **Never merge unless explicitly authorized and permitted by policy.**

## Done When

- [ ] GitHub Issue exists (reused or created) with reproduction steps and expected behavior.
- [ ] Bug reproduced and evidence recorded.
- [ ] Dedicated fix branch created from `main`.
- [ ] Regression test added where appropriate.
- [ ] Smallest safe fix implemented and reviewed.
- [ ] Tests pass locally.
- [ ] Branch pushed and a linked PR exists targeting `main`.
- [ ] CI status and review requirements reported.