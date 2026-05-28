import logging
import os
import secrets

AUTH_TOKEN_FILE_ENV = "SC4S_AUTH_TOKEN_FILE"

logger = logging.getLogger(__name__)


def _load_token() -> str:
    token_file = (os.environ.get(AUTH_TOKEN_FILE_ENV) or "").strip()
    if not token_file:
        return ""
    try:
        with open(token_file) as f:
            return f.read().strip()
    except OSError as exc:
        raise RuntimeError(
            f"Cannot read {AUTH_TOKEN_FILE_ENV}={token_file!r}: {exc}"
        ) from exc


class Sc4sTokenVerifier:
    def __init__(self, expected_token: str) -> None:
        if not expected_token or not expected_token.strip():
            raise ValueError("expected_token must be a non-empty string")
        self._expected_bytes = expected_token.encode("utf-8")

    def verify_token(self, token: str) -> bool:
        if not token or not token.strip():
            logger.warning("SC4S API auth: rejected request with missing token")
            return False

        try:
            presented = token.encode("utf-8")
        except (AttributeError, UnicodeEncodeError):
            logger.warning("SC4S API auth: rejected request with undecodable token")
            return False

        if not secrets.compare_digest(presented, self._expected_bytes):
            logger.warning("SC4S API auth: rejected request with invalid token")
            return False

        logger.info("SC4S API auth: accepted request")
        return True


def build_token_verify() -> Sc4sTokenVerifier | None:
    token = _load_token()
    if not token or not token.strip():
        logger.warning("Auth token disabled (%s not set)", AUTH_TOKEN_FILE_ENV)
        return None

    return Sc4sTokenVerifier(token)
