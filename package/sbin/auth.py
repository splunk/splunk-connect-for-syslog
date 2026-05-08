import logging
import os
import secrets

AUTH_TOKEN_ENV = "SC4S_AUTH_TOKEN"

logger = logging.getLogger(__name__)

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
    token = os.environ.get(AUTH_TOKEN_ENV, "")
    if not token or not token.strip():
        logger.info("Auth token disabled (%s not set)", AUTH_TOKEN_ENV)
        return None
    
    logger.info("Auth token enabled (%s set)", AUTH_TOKEN_ENV)
    return Sc4sTokenVerifier(token)