# MCP Development Environment Setup

This document describes the Model Context Protocol (MCP) server configuration for VS Code and Kilo Code in the `admin-template` monorepo.

## Integrations configured

| # | Integration | Transport | Purpose |
|---|-------------|-----------|---------|
| 1 | Context7 | stdio (local) | Current documentation for libraries, APIs, frameworks, packages |
| 2 | Playwright MCP | stdio (local) | Isolated browser automation and web app testing |
| 3 | Next.js DevTools MCP | stdio (local) | Next.js framework diagnostics and dev-server inspection |
| 4 | Dart/Flutter MCP | stdio (local) | Dart/Flutter diagnostics, testing, SDK tooling |
| 5 | PostgreSQL MCP | stdio (local) | Read-only access to the local development database |
| 6 | GitHub MCP | HTTP (remote) | Repository and issue inspection (read-only) |

## Configuration files

| File | Client | Format |
|------|--------|--------|
| `.vscode/mcp.json` | VS Code (workspace) | VS Code MCP schema (`servers`, `inputs`) |
| `kilo.jsonc` | Kilo Code (project) | Kilo MCP schema (`mcp`, `type: local/remote`) |
| `.env.mcp.example` | Kilo Code / shell | Sanitized example env values (safe to commit) |
| `.env.mcp.local` | Kilo Code / shell | Real secret values (gitignored, `chmod 600`) |

VS Code and Kilo Code use **different** configuration formats and **do not share** a config file. Both are configured with the same six integrations.

## Prerequisites

- Node.js v26.9.0, pnpm 11.25.0 (monorepo package manager)
- Dart SDK 3.13.5, Flutter 3.47.7 (at `~/Documents/flutter`)
- PostgreSQL 16 (Homebrew `postgresql@16`)
- uv 0.12.19 (Python dependency management, `apps/api`)
- Docker 29.8.2

## Per-integration setup

### 1. Context7

- Package: `@upstash/context7-mcp@4.4.2` (npx, stdio)
- Command: `npx -y @upstash/context7-mcp@4.4.2`
- Authentication: optional `CONTEXT7_API_KEY` (get at context7.com/dashboard). Works unauthenticated at a lower rate limit.
- VS Code: no input required by default; add `CONTEXT7_API_KEY` to `.env.mcp.local` / shell env for higher rate limits.
- Kilo Code: `type: "local"`, `command: ["npx", "-y", "@upstash/context7-mcp@4.4.2"]`
- Tools: `resolve-library-id`, `query-docs`

### 2. Playwright MCP

- Package: `@playwright/mcp@0.0.83` (npx, stdio)
- Command: `npx -y @playwright/mcp@0.0.83 --headless`
- Chromium browser: available in `~/Library/Caches/ms-playwright/chromium-1248`
- Isolated, headless browser sessions only. Do not reuse personal profiles or log into external accounts.
- Tools: 25 browser automation tools (`browser_navigate`, `browser_click`, `browser_take_screenshot`, etc.)

### 3. Next.js DevTools MCP

- Package: `next-devtools-mcp@0.4.0` (npx, stdio)
- Command: `npx -y next-devtools-mcp@0.4.0`
- Requires Next.js 16+ (installed: 16.4.0) with a running dev server (`pnpm dev` in `apps/web`).
- The dev server exposes `/_next/mcp` by default (`experimental.mcpServer` not disabled in `next.config.ts`).
- Connects to the running dev server at runtime; `nextjs_index`/`nextjs_call` need `pnpm dev` running.
- Tools: `nextjs_index`, `nextjs_call`, `nextjs_docs`, `browser_eval`

### 4. Dart/Flutter MCP

- Official SDK command: `dart mcp-server` (stdio)
- Dart 3.13.5, Flutter 3.47.7 (both ≥ required 3.9 / 3.35)
- Command: `dart mcp-server`
- This is the SDK-provided MCP server; no unofficial substitute is used.
- Exposes tools only when the client supports and provides Roots (workspace folders). Configure your client to expose the repo root (and `apps/mobile` for Flutter) as roots.
- Tools: analyzer, pub, tests, DTD, widget inspector, etc. (when roots are provided)

### 5. PostgreSQL MCP

- Package: `pg-ro-mcp@0.1.0` (npx, stdio) — maintained read-only fork of the deprecated `@modelcontextprotocol/server-postgres@0.6.2`
- Command: `npx -y pg-ro-mcp@0.1.0 --database-url <URL>`
- Local development database: PostgreSQL 16 running on `localhost:5432` (Homebrew `postgresql@16`, trust auth)
- Database: `postgres` (empty, owned by `tiago`) — or `creator_intelligence` (existing tables)
- Connection string comes from `MCP_POSTGRES_URL` (env var or VS Code input) — never hardcoded
- Read-only enforcement: server runs every query in a `READ ONLY` transaction
- **Database-side permissions:** create a dedicated least-privilege read-only role and grant `USAGE` on schema + `SELECT` on tables. This requires explicit approval — no grants/role changes are applied automatically.
- Configure the URL in `.env.mcp.local` (Kilo) or via the VS Code input prompt.

### 6. GitHub MCP

- Remote server: `https://api.githubcopilot.com/mcp/readonly` (HTTP)
- Read-only mode: `X-MCP-Readonly: true` header + `/readonly` URL path
- Toolsets: `repos,issues,pull_requests`
- Authentication: fine-grained personal access token (read-only, repo-scoped) via `Authorization: Bearer` header
- Token source: `MCP_GITHUB_PAT` env var (Kilo) or VS Code input prompt — never hardcoded
- Create a fine-grained PAT at github.com/settings/tokens/personal-access-tokens/fine-grained with read access to the required repositories only.
- No repository changes are made through GitHub MCP during setup.

## Authentication and secrets

- No credentials or tokens are hardcoded in any configuration file.
- VS Code uses `inputs` of type `promptString` (password) — you are prompted for secrets when VS Code starts.
- Kilo Code uses `{env:VARIABLE_NAME}` interpolation — set values in `.env.mcp.local` and source it before launching Kilo, or export them in your shell.
- `.env.mcp.example` contains placeholder values only and is safe to commit.
- `.env.mcp.local` holds real values, is `chmod 600`, and is gitignored.
- `.gitignore` explicitly ignores `.env.mcp.local` and un-ignores `.env.mcp.example`.

To activate Kilo Code secrets:
```sh
# copy example, fill in real values, then source
cp .env.mcp.example .env.mcp.local
chmod 600 .env.mcp.local
# edit .env.mcp.local with real values, then:
set -a; . .env.mcp.local; set +a
# then launch Kilo Code
```

## Enabling / disabling integrations

- VS Code: edit `.vscode/mcp.json` and set a server's entry, or toggle via VS Code settings (MCP).
- Kilo Code: edit `kilo.jsonc` and set `"enabled": false` on a server, or disable via Kilo Settings → MCP servers.
- Disabling a server does not remove it; it only prevents it from starting on launch.

## Troubleshooting

| Issue | Likely cause | Action |
|-------|--------------|--------|
| Server fails to start | Missing executable on PATH (macOS GUI) | Ensure `dart`, `flutter`, `npx` are on PATH; VS Code GUI may need `terminal.integrated.env.osx` configured |
| Context7 rate-limited | No API key | Add `CONTEXT7_API_KEY` to `.env.mcp.local` / shell env |
| PostgreSQL connection refused | Postgres not running | `brew services start postgresql@16` |
| PostgreSQL permission denied | No read-only role/grants | Create a read-only role and grant SELECT (requires approval) |
| GitHub tools missing / 401 | Missing or wrong PAT | Set `MCP_GITHUB_PAT` with a fine-grained read-only token |
| Dart shows 0 tools | Client doesn't provide Roots | Configure workspace roots in your MCP client (repo root + apps/mobile) |
| Next.js DevTools no server info | Dev server not running | Run `pnpm dev` in `apps/web`, then use `nextjs_index`/`nextjs_call` |
| Playwright browser won't launch | Chromium missing | `npx playwright install chromium` (Chromium already cached) |

## Validation status

- Context7: PASS — handshake + `query-docs` invocation verified
- Playwright: PASS — handshake + headless browser launch + screenshot verified
- PostgreSQL: PASS — handshake + read-only `SELECT` invocation verified
- Next.js DevTools: PARTIAL — server + handshake verified; E2E needs a running dev server
- Dart/Flutter: PARTIAL — server starts + handshake verified; tool listing requires a Roots-supporting client
- GitHub: BLOCKED — configured but requires a fine-grained PAT credential to validate

## Version pins

| Integration | Package | Version | Reason |
|-------------|---------|---------|--------|
| Context7 | `@upstash/context7-mcp` | 4.4.2 | Verified latest via npm; pinned for reproducibility |
| Playwright | `@playwright/mcp` | 0.0.83 | Verified latest via npm |
| Next.js DevTools | `next-devtools-mcp` | 0.4.0 | Verified latest via npm; requires Next.js 16+ |
| PostgreSQL | `pg-ro-mcp` | 0.1.0 | Supported read-only alternative to deprecated `server-postgres@0.6.2` |
| Dart/Flutter | SDK `dart mcp-server` | Dart 3.13.5 | Official SDK command; no separate package |
| GitHub | remote `api.githubcopilot.com` | n/a | Official remote GitHub MCP server (read-only) |
