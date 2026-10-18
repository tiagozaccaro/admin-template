---
name: monorepo-workflow
description: pnpm + Turbo monorepo workflow for admin-template. Use when editing shared packages, app boundaries, scripts, dependencies, or running build/lint/typecheck across workspaces. Covers workspace topology, task graph, scoped commands, and cross-package impact.
---

# Monorepo Workflow

## Topology
- Workspaces: apps/*, packages/*
- Apps: apps/web (Next.js 16), apps/api (FastAPI), apps/mobile (Flutter).
- Shared packages: packages/ui, packages/eslint-config, packages/typescript-config.
- Commands run from root package.json use Turbo.

## Commands
- Install: `pnpm install`; API dependencies use `pnpm install` in apps/api (runs `uv sync`).
- Checks: `pnpm lint`, `pnpm typecheck`, `pnpm build`, `pnpm format`.
- Scoped checks: `pnpm --filter @admin-template/web typecheck`, `pnpm --filter @admin-template/api test`.
- API task graph uses scripts in apps/api/package.json (ruff, pyright, pytest, uv lock --check).
- Web checks use apps/web scripts: eslint, prettier, tsc --noEmit.

## Rules
- Identify downstream consumers before modifying packages/ui.
- Prefer workspace imports (`@workspace/*`) over relative cross-package paths.
- Do not edit generated lockfiles manually; run lock generation commands.
- TypeScript strictness comes from packages/typescript-config; do not bypass project references.
- Web Next.js 16 has breaking changes; consult `node_modules/next/dist/docs` before nontrivial changes.
- Turbo caching: declare outputs correctly; new persistent processes need `cache: false`.
- Never assume pnpm differs from yarn/npm conventions.
