"""Template MCP server — minimum boilerplate to deploy on Render.

Copy this file, rename the server, and add your tools. Deploy with:
    Build:  pip install -e .
    Start:  python mcp_server.py
    Health: GET /health
"""

from __future__ import annotations

import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Line buffering so logs print instantly in cloud control panels
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Explicit transport security: the SDK auto-enables DNS rebinding protection
# with localhost-only allowed_hosts when transport_security is None AND the
# default host is 127.0.0.1 — which 421s production Host headers (Render's
# <service>.onrender.com) and rejects remote clients. Set MCP_ALLOWED_HOSTS
# to your deployed domain.
mcp: FastMCP = FastMCP(
    "Template",
    instructions="Describe when the client should use each tool.",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=(
            os.environ.get("MCP_ENABLE_DNS_REBINDING_PROTECTION", "true").lower()
            not in ("false", "0", "no", "off")
        ),
        allowed_hosts=[
            h.strip()
            for h in os.environ.get("MCP_ALLOWED_HOSTS", "localhost:*,127.0.0.1:*").split(",")
            if h.strip()
        ],
        allowed_origins=[
            o.strip()
            for o in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",")
            if o.strip()
        ],
    ),
)


@mcp.tool()
def example_tool(query: str) -> dict[str, Any]:
    """Replace with your first tool.

    Args:
        query: Example argument.
    """
    return {"query": query}


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    """Health check endpoint for hosting platforms (Render)."""
    return JSONResponse({"status": "healthy", "mcp_endpoint": "/mcp"})


def main() -> None:
    """Serve the streamable-HTTP MCP transport at /mcp, binding env HOST/PORT."""
    mcp.settings.host = os.environ.get("HOST", "0.0.0.0")
    mcp.settings.port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
