"""MCP tool for sending raw-text syslog events."""

import socket
from typing import Literal

from app import mcp
from utils.syslog_sender import send_text


@mcp.tool
def send_syslog_text(
    text: str,
    protocol: Literal["tcp", "udp"] = "udp",
    port: int = 514,
    framing: Literal["raw", "newline", "octet-counting"] | None = None,
    timeout_seconds: float = 5.0,
) -> dict:
    """Send each non-empty line of raw syslog text to the SC4S API host."""
    try:
        return send_text(
            text=text,
            protocol=protocol,
            port=port,
            framing=framing,
            timeout=timeout_seconds,
        )
    except ValueError as error:
        return {"status": "error", "error": "invalid_request", "message": str(error)}
    except socket.timeout as error:
        return {"status": "error", "error": "connection_timeout", "message": str(error)}
    except ConnectionRefusedError as error:
        return {"status": "error", "error": "connection_refused", "message": str(error)}
    except OSError as error:
        return {"status": "error", "error": "socket_error", "message": str(error)}