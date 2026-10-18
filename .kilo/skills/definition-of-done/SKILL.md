---
name: definition-of-done
description: Completion checklist for admin-template tasks. Use before declaring any feature, bug fix, or refactor complete; requires relevant checks, honest failure reporting, security review, and scope validation.
---

# Definition of Done

## Before complete
- Scope verified against user request; no speculative changes.
- Relevant checks run and reported honestly: pass/fail/skip/blocked.
- For web: lint + typecheck; for api: ruff + pyright + pytest (+ uv lock --check when deps change); for mobile: analyze + format + test.
- Monorepo cross-package changes validated at root.
- No secrets or credentials in diff.
- Accessible UI changes and strict types preserved.
- Migration changes follow secure DB workflow.
- Final diff reviewed mentally.
