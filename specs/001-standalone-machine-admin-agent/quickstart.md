# Quickstart

1. Start core API and web.
2. Run agent daemon: `cd apps/agent && uv run uvicorn admin_template_agent.main:app --port 8100`.
3. Register agent in web: Agents page -> Add agent (url http://localhost:8100, token).
4. Open chat, select agent, send message; verify streamed response.
5. Request destructive action; verify approval prompt and audit log.