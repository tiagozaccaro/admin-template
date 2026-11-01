"""Agent daemon entrypoint.

Exposes a FastAPI app with the chat, config, tools, and session endpoints
described in contracts/api.md. Run with:

    uvicorn admin_template_agent.main:app --port 8100
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_template_agent.config import config
from admin_template_agent.routers.approvals import router as approvals_router
from admin_template_agent.routers.chat import router as chat_router

logging.basicConfig(level=config.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    logger.info(
        "Agent daemon starting (name=%s, model=%s, port=%d)",
        config.agent_name,
        config.model,
        config.port,
    )
    yield
    logger.info("Agent daemon stopping")


app = FastAPI(
    title="Admin Template Agent",
    version="0.1.0",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(approvals_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def main() -> None:
    """Run the agent daemon with uvicorn."""
    import uvicorn

    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()


__all__ = ["app", "main"]
