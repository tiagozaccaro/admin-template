---
description: Review a pull request diff, linked Issue, acceptance criteria, security, error handling, tests, and CI results. Read-only: never modify files or approve/merge.
---

## User Input

```text
$ARGUMENTS
```

## Pre-Execution Checks

1. Confirm GitHub CLI authentication (`gh auth status`) and repository access.
2. Identify the PR number from the input. If none is given, use `gh pr list --repo <owner>/<repo> --limit 10` to ask the user to pick one.

## Outline

1. **Review the PR diff**
   - Fetch the diff: `gh pr diff <NUMBER>`.
   - Inspect the linked Issue and its acceptance criteria.
   - Check for correctness, security, error handling, boundaries, tests, and performance.
2. **Report findings by severity**
   - Use severity levels: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`.
   - Include file and line references where possible.
3. **Check CI results**
   - Inspect the PR's CI status: `gh pr checks <NUMBER>`.
   - Report which checks passed, failed, or are pending.
4. **Verify acceptance criteria**
   - Map each acceptance criterion to the diff and CI results.
   - Report which criteria are satisfied and which are not.

## Constraints

- **Read-only**: do not modify files, approve, or merge the PR in review-only mode.
- Do not bypass required checks, approvals, or branch rules.
- A code-review agent may provide findings, but its review is not a substitute for required human approval.

## Done When

- [ ] PR diff, linked Issue, and acceptance criteria reviewed.
- [ ] Findings reported by severity with file:line references.
- [ ] CI results inspected and reported.
- [ ] No files modified, no approval or merge performed.