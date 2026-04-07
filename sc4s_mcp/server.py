import os
import sys

from app import mcp

import resources.docs  # noqa: F401
import resources.tools  # noqa: F401

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse" if "--sse" in sys.argv else "stdio")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    if transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run()
