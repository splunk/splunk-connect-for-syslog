import logging
import os

from app import mcp

from sc4s_mcp.utils.transport import TransportMode, resolve_transport

import resources.docs  # noqa: F401
import tools.configuration_tools  # noqa: F401
import tools.metadata_tools  # noqa: F401
import prompts.workflows  # noqa: F401

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    transport = resolve_transport()
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    if transport == TransportMode.HTTP:
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()
