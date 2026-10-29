# API Contracts

## Agent Registry (core API)
- POST /api/v1/agents {name,url,token} -> Agent
- GET /api/v1/agents -> list
- GET /api/v1/agents/{id} -> Agent
- PATCH /api/v1/agents/{id} -> Agent
- DELETE /api/v1/agents/{id} -> 204
- POST /api/v1/agents/{id}/health -> {status}

## Agent Daemon
- GET /health -> {status}
- GET /models -> list
- POST /chat/agent {prompt_input,model,session_id} -> SSE stream
- GET /tools -> list
- GET/PUT /config -> config
- GET /sessions/{id} -> history