import logging
import os
import sys

from fastapi import FastAPI
import uvicorn

from app import mcp
from tls import TlsConfigError, build_uvicorn_ssl_kwargs
from utils.transport import TransportMode, resolve_transport

import resources.docs  # noqa: F401
import tools.configuration_tools  # noqa: F401
import tools.metadata_tools  # noqa: F401
import prompts.workflows  # noqa: F401


logger = logging.getLogger(__name__)

HEALTH_PATH = "/health"
DEFAULT_PORT = "8000"
MCP_MOUNT_PATH = "/mcp"


def _build_api() -> FastAPI: 
    mcp_app = mcp.http_app(path="/")
    api = FastAPI(lifespan=mcp_app.lifespan)

    @api.get(HEALTH_PATH, include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    api.mount(MCP_MOUNT_PATH, mcp_app)
    return api


def _run_http() -> int:
    api = _build_api()

    try:
        ssl_kwargs = build_uvicorn_ssl_kwargs()
    except TlsConfigError as exc:
        logger.error("TLS configuration error: %s", exc)
        return 1

    if ssl_kwargs:
        logger.info("MCP TLS enabled")

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", DEFAULT_PORT))

    uvicorn.run(api, host=host, port=port, **ssl_kwargs)
    return 0


def _run_stdio() -> int:
    mcp.run()
    return 0


def main() -> int:
    if resolve_transport() == TransportMode.HTTP:
        return _run_http()
    return _run_stdio()


if __name__ == "__main__":
    sys.exit(main())
