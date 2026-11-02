"""MCP (Model Context Protocol) client.

Discovers and aggregates tools from configured MCP servers at runtime so the
agent can call tools exposed by external services. Uses the MCP Python SDK
when available, falling back to a minimal SSE-based client otherwise.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from admin_template_agent.config import config

logger = logging.getLogger(__name__)


class MCPClient:
    """Lightweight MCP client that connects to servers over SSE/HTTP."""

    def __init__(self, servers: list[str] | None = None) -> None:
        self.servers: list[str] = list(servers or config.mcp_servers or [])
        self._tools: dict[str, list[dict[str, Any]]] = {}
        self._connected: bool = False

    async def connect(self) -> None:
        """Connect to all configured MCP servers and cache their tools."""
        self._tools = {}
        for server in self.servers:
            try:
                tools = await self._list_tools(server)
                self._tools[server] = tools
                logger.info("MCP server %s: %d tools", server, len(tools))
            except Exception:
                logger.exception("Failed to connect to MCP server %s", server)
                self._tools[server] = []
        self._connected = True

    async def _list_tools(self, server: str) -> list[dict[str, Any]]:
        """List tools exposed by a single MCP server.

        Prefers the official MCP Python SDK when installed; falls back to a
        plain HTTP probe of the server's /tools endpoint.
        """
        try:
            from mcp import ClientSession  # type: ignore
            from mcp.client.sse import sse_client  # type: ignore
        except Exception:
            return await self._http_list_tools(server)

        try:
            async with sse_client(server) as (read, write):  # type: ignore
                async with ClientSession(read, write) as session:  # type: ignore
                    await session.initialize()
                    result = await session.list_tools()
                    return [t.model_dump() for t in result.tools]
        except Exception:
            logger.debug("MCP SDK path failed for %s, trying HTTP", server)
            return await self._http_list_tools(server)

    async def _http_list_tools(self, server: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(server.rstrip("/") + "/tools")
            if resp.status_code != 200:
                return []
            data = resp.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "tools" in data:
                return data["tools"]
        return []

    @property
    def connected(self) -> bool:
        return self._connected

    def all_tools(self) -> list[dict[str, Any]]:
        """Return all discovered tools across all servers."""
        tools: list[dict[str, Any]] = []
        for server, server_tools in self._tools.items():
            for tool in server_tools:
                tool = dict(tool)
                tool.setdefault("server", server)
                tools.append(tool)
        return tools

    def tool_names(self) -> list[str]:
        return [t.get("name", "") for t in self.all_tools()]


def mcp_client(servers: list[str] | None = None) -> MCPClient:
    """Construct an MCP client for the given servers (or configured ones)."""
    return MCPClient(servers=servers)


__all__ = ["MCPClient", "mcp_client"]
