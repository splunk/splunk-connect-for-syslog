import logging
import os
import secrets

AUTH_TOKEN_ENV = "SC4S_AUTH_TOKEN"
AUTH_TOKEN_FILE_ENV = "SC4S_AUTH_TOKEN_FILE"

logger = logging.getLogger(__name__)


def _load_token() -> str:
    token_file = (os.environ.get(AUTH_TOKEN_FILE_ENV) or "").strip()
    if token_file:
        try:
            return open(token_file).read().strip()
        except OSError as exc:
            raise RuntimeError(
                f"Cannot read {AUTH_TOKEN_FILE_ENV}={token_file!r}: {exc}"
            ) from exc
    return os.environ.get(AUTH_TOKEN_ENV, "")


class Sc4sTokenVerifier:
    def __init__(self, expected_token: str) -> None:
        if not expected_token or not expected_token.strip():
            raise ValueError("expected_token must be a non-empty string")
        self._expected_bytes = expected_token.encode("utf-8")

    def verify_token(self, token: str) -> bool:
        if not token or not token.strip():
            return False

        try:
            presented = token.encode("utf-8")
        except (AttributeError, UnicodeEncodeError):
            return False

        if not secrets.compare_digest(presented, self._expected_bytes):
            return False

        return True


def build_token_verify() -> Sc4sTokenVerifier | None:
    token = _load_token()
    if not token or not token.strip():
        logger.warning("Auth token disabled (%s / %s not set)", AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV)
        return None

    return Sc4sTokenVerifier(token)