"""Token authentication for the SC4S MCP server.

Authentication is enabled only when the ``SC4S_MCP_AUTH_TOKEN`` environment
variable is set to a non-empty value. When enabled, every request to the HTTP
transport must carry an ``Authorization: Bearer <token>`` header matching the
configured value. When the variable is unset/empty,
``build_auth_provider()`` returns ``None`` and FastMCP runs unauthenticated.
"""

import logging
import secrets

from fastmcp.server.auth import AccessToken, AuthProvider, TokenVerifier

from utils.token_utils import load_token

AUTH_TOKEN_ENV = "SC4S_MCP_AUTH_TOKEN"
AUTH_TOKEN_FILE_ENV = "SC4S_MCP_AUTH_TOKEN_FILE"
_CLIENT_ID = "sc4s-mcp-client"

logger = logging.getLogger(__name__)


class StaticBearerTokenVerifier(TokenVerifier):
    def __init__(self, expected_token: str) -> None:
        if not expected_token or not expected_token.strip():
            raise ValueError("expected_token must be a non-empty string")
        super().__init__()
        self._expected_bytes = expected_token.encode("utf-8")

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or not token.strip():
            logger.warning("MCP auth: rejected request with missing token")
            return None

        try:
            presented = token.encode("utf-8")
        except (AttributeError, UnicodeEncodeError):
            logger.warning("MCP auth: rejected request with undecodable token")
            return None

        if not secrets.compare_digest(presented, self._expected_bytes):
            logger.warning("MCP auth: rejected request with invalid token")
            return None

        logger.info("MCP auth: accepted request for client %s", _CLIENT_ID)
        return AccessToken(
            token=token,
            client_id=_CLIENT_ID,
            scopes=[],
            expires_at=None,
        )


def build_auth_provider() -> AuthProvider | None:
    token = load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV)
    if not token or not token.strip():
        logger.info(
            "MCP bearer auth disabled (%s / %s not set)",
            AUTH_TOKEN_ENV,
            AUTH_TOKEN_FILE_ENV,
        )
        return None

    return StaticBearerTokenVerifier(token)
