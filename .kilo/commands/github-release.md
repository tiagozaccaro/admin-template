---
description: Verify a squash-merged PR, expected checks, deployment status, then update the Issue and release notes. Never mark unverified deployment steps as successful.
---

## User Input

```text
$ARGUMENTS
```

## Pre-Execution Checks

1. Confirm GitHub CLI authentication (`gh auth status`) and repository access.
2. Identify the PR number from the input. If none is given, use `gh pr list --repo <owner>/<repo> --limit 10` to ask the user to pick one.
3. Confirm the PR targets `main` and was merged via **Squash and merge**.

## Outline

1. **Verify the PR was squash-merged**
   - Inspect the merge commit: `gh pr view <NUMBER> --json mergeCommit,mergeState,mergedBy,mergedAt`.
   - Confirm `mergeState` is `MERGED` and the merge method was squash.
2. **Verify the expected checks passed**
   - Inspect the PR's CI status: `gh pr checks <NUMBER>`.
   - Confirm all required checks passed before the merge.
   - If any check failed, report it and halt.
3. **Confirm deployment status, if configured**
   - Inspect the deployment workflow run: `gh run list --branch main --limit 5`.
   - **Never mark unverified deployment steps as successful.**
   - If CD is not configured or the deployment job is disabled (see `.github/workflows/cd.yml`), report that deployment is not applicable or pending.
4. **Update the Issue and release notes where appropriate**
   - Link the PR to the Issue using closing keywords (e.g., `Closes #ISSUE_NUMBER`).
   - Update the Issue status to reflect reality (closed only when completion criteria are satisfied).
   - Update release notes if a changelog or release draft is configured.
5. **Cut the release tag when a release is requested**
   - Only with explicit authorization, tag the merge commit: `git tag v<semver>` and `git push origin v<semver>`.
   - The tag triggers the `release` workflow (`.github/workflows/release.yml`), which builds the web bundle, pushes the container images to `ghcr.io`, and publishes the GitHub release.
   - Report the workflow run and the release URL; never report a release as published before the workflow succeeded.
6. **Delete the feature branch only when it is safe and permitted**
   - Confirm `delete_branch_on_merge` is enabled on the repository.
   - Delete the branch: `gh pr delete <NUMBER>` or `git push origin --delete <branch>` only with explicit authorization.

## Done When

- [ ] PR verified as squash-merged into `main`.
- [ ] Expected CI checks verified as passed.
- [ ] Deployment status reported accurately (deployed / not applicable / pending / failed).
- [ ] Issue status updated to reflect reality.
- [ ] Release notes updated where appropriate.