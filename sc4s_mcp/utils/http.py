import logging
import os

import httpx

from utils.token_utils import load_token

logger = logging.getLogger(__name__)

SC4S_API_URL = os.getenv("SC4S_API_URL", "http://localhost:8080")
SC4S_API_TOKEN_ENV = "SC4S_API_TOKEN"
SC4S_API_TOKEN_FILE_ENV = "SC4S_API_TOKEN_FILE"
SC4S_API_CA_CERT_ENV = "SC4S_API_CA_CERT"


def _auth_headers() -> dict[str, str]:
    token = load_token(SC4S_API_TOKEN_ENV, SC4S_API_TOKEN_FILE_ENV)
    if token and token.strip():
        return {"Authorization": f"Bearer {token}"}
    return {}


def _verify() -> bool | str:
    """Return the CA cert path for TLS verification, or True to use system CAs."""
    ca_cert = (os.environ.get(SC4S_API_CA_CERT_ENV) or "").strip()
    return ca_cert if ca_cert else True


def sc4s_request(method: str, path: str, **kwargs) -> dict:
    """Execute an HTTP request against the SC4S API with unified error handling."""
    url = f"{SC4S_API_URL}{path}"
    headers = {**_auth_headers(), **kwargs.pop("headers", {})}
    if headers:
        kwargs["headers"] = headers
    kwargs.setdefault("verify", _verify())
    kwargs.setdefault("timeout", 5.0)
    logger.debug("SC4S API %s %s", method.upper(), url)
    try:
        resp = getattr(httpx, method)(url, **kwargs)
        resp.raise_for_status()
        logger.debug("SC4S API %s %s -> %s", method.upper(), url, resp.status_code)
        return resp.json()
    except httpx.ConnectError:
        logger.error(
            "SC4S API %s %s -> connection error (unreachable)", method.upper(), url
        )
        return {
            "status": "error",
            "message": f"SC4S instance unreachable at {SC4S_API_URL}",
        }
    except httpx.TimeoutException:
        logger.error("SC4S API %s %s -> timeout", method.upper(), url)
        return {"status": "error", "message": f"Request to {url} timed out"}
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
        except Exception:
            body = {"detail": e.response.text}
        logger.error(
            "SC4S API %s %s -> %s %s", method.upper(), url, e.response.status_code, body
        )
        return {"status": "error", "http_status": e.response.status_code, **body}
    except httpx.HTTPError as e:
        logger.error("SC4S API %s %s -> %s", method.upper(), url, e)
        return {"status": "error", "message": str(e)}
