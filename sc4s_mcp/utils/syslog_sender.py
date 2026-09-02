"""Small raw-text syslog sender used by the MCP event tool."""

import os
import socket
import time
from urllib.parse import urlparse

DEFAULT_ALLOWED_PORTS = {514, 601}
MAX_EVENT_BYTES = 65_507

def _host():
    hostname = urlparse(os.getenv("SC4S_API_URL", "")).hostname
    if not hostname:
        raise ValueError("SC4S_API_URL must contain a hostname")
    return hostname


def _validate(port, timeout, protocol, framing):
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65_535:
        raise ValueError("port must be an integer between 1 and 65535")
    allowed = os.getenv("SC4S_MCP_ALLOWED_SYSLOG_PORTS", "514,601")
    if allowed != "*" and port not in {int(value.strip()) for value in allowed.split(",")}:
        raise ValueError(f"port {port} is not allowed for MCP syslog sending")
    if not isinstance(timeout, (int, float)) or not 0.1 <= timeout <= 30:
        raise ValueError("timeout must be between 0.1 and 30 seconds")
    if protocol not in {"tcp", "udp"}:
        raise ValueError("protocol must be tcp or udp")
    if protocol == "udp" and framing not in {None, "raw"}:
        raise ValueError("UDP framing must be raw")
    if protocol == "tcp" and framing not in {None, "newline", "octet-counting"}:
        raise ValueError("TCP framing must be newline or octet-counting")


def _payloads(text):
    payloads = [line.encode("utf-8") for line in text.splitlines() if line.strip()]
    if not payloads:
        raise ValueError("No syslog events found in raw text input")
    if any(len(payload) > MAX_EVENT_BYTES for payload in payloads):
        raise ValueError("event exceeds maximum size of 65507 bytes")
    return payloads


def send_text(*, text, protocol, port, framing=None, timeout=5.0):
    """Send each non-empty line in *text* to the configured SC4S host."""
    protocol = protocol.lower()
    _validate(port, timeout, protocol, framing)
    payloads = _payloads(text)
    if framing is None:
        framing = "raw" if protocol == "udp" else "newline"
    destination = (_host(), port)
    started = time.monotonic()
    sock = None
    sent = failed = bytes_sent = 0
    try:
        if protocol == "tcp":
            sock = socket.create_connection(destination, timeout=timeout)
            for payload in payloads:
                framed = (
                    f"{len(payload)} ".encode("ascii") + payload
                    if framing == "octet-counting"
                    else payload + b"\n"
                )
                try:
                    sock.sendall(framed)
                except OSError:
                    failed += 1
                else:
                    sent += 1
                    bytes_sent += len(framed)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            for payload in payloads:
                try:
                    bytes_sent += sock.sendto(payload, destination)
                except OSError:
                    failed += 1
                else:
                    sent += 1
    finally:
        if sock:
            sock.close()
    return {
        "status": "ok" if failed == 0 else "partial",
        "attempted": len(payloads),
        "sent": sent,
        "failed": failed,
        "bytes_sent": bytes_sent,
        "protocol": protocol,
        "framing": framing,
        "port": port,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
    }
