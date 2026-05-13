"""Container-side liveness probe for the SC4S MCP server."""

import os
import ssl
import sys
import urllib.request

from sc4s_mcp import tls
from sc4s_mcp.server import DEFAULT_PORT, HEALTH_PATH

_TIMEOUT_SEC = 3


def _build_url() -> str:
    port = os.environ.get("MCP_PORT") or DEFAULT_PORT
    scheme = "https" if tls.tls_is_enabled() else "http"
    return f"{scheme}://localhost:{port}{HEALTH_PATH}"


def main() -> int:
    url = _build_url()
    ctx = ssl._create_unverified_context() if url.startswith("https://") else None
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT_SEC, context=ctx) as resp:
            return 0 if resp.status == 200 else 1
    except Exception as e:
        print(f"Healthcheck request exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
