# Admin Template Guidelines

Read `AGENTS.md` before writing any code in this repository. It holds the engineering
standards for the monorepo (Next.js 16 web app, FastAPI API, Flutter mobile app) and the
rules that apply to every change.

Key points:

- The FastAPI API in `apps/api` is authoritative; web and mobile only consume it.
- Strict TypeScript (no `any`), explicit Python types with Pydantic validation at the
  API boundary.
- pnpm + Turbo for JS/TS, uv for Python, Flutter for mobile. One lockfile per ecosystem.
- Never commit directly to `main`; every change needs a branch and a pull request.
- Commit messages follow Conventional Commits; `commitlint` enforces them in CI.
- Never claim a check passed unless it actually ran.
