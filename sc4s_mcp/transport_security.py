"""Host and Origin validation for the MCP HTTP transport."""

import logging
import os
from collections.abc import Iterable
from urllib.parse import urlsplit

from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send


logger = logging.getLogger(__name__)

ALLOWED_HOSTS_ENV = "SC4S_MCP_ALLOWED_HOSTS"
ALLOWED_ORIGINS_ENV = "SC4S_MCP_ALLOWED_ORIGINS"
DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "[::1]")


def _parse_csv(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def _parse_host(value: str) -> tuple[str, int | None]:
    try:
        parsed = urlsplit(f"//{value}")
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"invalid host value: {value!r}") from exc

    if not hostname or parsed.username or parsed.password or parsed.path:
        raise ValueError(f"invalid host value: {value!r}")

    return hostname.lower().rstrip("."), port


def _parse_origin(value: str) -> tuple[str, str, int | None]:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"invalid origin value: {value!r}") from exc

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"invalid origin value: {value!r}")

    return parsed.scheme.lower(), parsed.hostname.lower().rstrip("."), port




class TransportSecurityMiddleware:
    """Reject HTTP requests whose Host or Origin is not explicitly trusted."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        host_values = [
            *DEFAULT_ALLOWED_HOSTS,
            *_parse_csv(os.getenv(ALLOWED_HOSTS_ENV)),
        ]
        self.allowed_hosts = tuple(_parse_host(value) for value in host_values)
        self.allowed_origins = tuple(
            _parse_origin(value)
            for value in _parse_csv(os.getenv(ALLOWED_ORIGINS_ENV))
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        host_header = headers.get("host", "")
        try:
            host = _parse_host(host_header)
        except ValueError:
            host = None

        if host is None or not self._host_allowed(host):
            logger.warning("MCP HTTP request rejected: disallowed Host %r", host_header)
            response = PlainTextResponse("Invalid Host header", status_code=421)
            await response(scope, receive, send)
            return

        origin_header = headers.get("origin")
        if origin_header:
            try:
                origin = _parse_origin(origin_header)
            except ValueError:
                origin = None

            if origin is None or origin not in self.allowed_origins:
                logger.warning(
                    "MCP HTTP request rejected: disallowed Origin %r", origin_header
                )
                response = PlainTextResponse("Invalid Origin header", status_code=403)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


    def _host_allowed(
        self,
        host: tuple[str, int | None]
    ) -> bool:
        hostname, port = host
        return any(
            hostname == allowed_hostname
            and (allowed_port is None or allowed_port == port)
            for allowed_hostname, allowed_port in self.allowed_hosts
        )
