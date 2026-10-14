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
    """Send each non-empty syslog line to the host configured by SC4S_API_URL.

    Args:
        text: Raw syslog events, one per line.
        protocol: udp (default) or tcp.
        port: Allowed destination port (default 514).
        framing: raw for UDP; newline or octet-counting for TCP.
            Defaults to raw for UDP and newline for TCP.
        timeout_seconds: Socket timeout, 0.1-30 seconds (default 5).

    Returns:
        Dict with status (ok/partial), send counts and transport details,
        or status=error and error details. Sending does not verify ingestion.
    """
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
