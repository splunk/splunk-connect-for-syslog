import os

import httpx

SC4S_API_URL = os.getenv("SC4S_API_URL", "http://localhost:8080")
SC4S_API_TOKEN_ENV = "SC4S_API_TOKEN"

_METHODS = {
    "get": httpx.get,
    "post": httpx.post,
    "put": httpx.put,
    "delete": httpx.delete,
}


def _auth_headers() -> dict[str, str]:
    token = os.environ.get(SC4S_API_TOKEN_ENV, "")
    if token and token.strip():
        return {"Authorization": f"Bearer {token}"}
    return {}


def sc4s_request(method: str, path: str, **kwargs) -> dict:
    """Execute an HTTP request against the SC4S API with unified error handling."""
    url = f"{SC4S_API_URL}{path}"
    headers = {**_auth_headers(), **kwargs.pop("headers", {})}
    if headers:
        kwargs["headers"] = headers
    try:
        resp = _METHODS[method](url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        return {
            "status": "error",
            "message": f"SC4S instance unreachable at {SC4S_API_URL}",
        }
    except httpx.TimeoutException:
        return {"status": "error", "message": f"Request to {url} timed out"}
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
        except Exception:
            body = {"detail": e.response.text}
        return {"status": "error", "http_status": e.response.status_code, **body}
    except httpx.HTTPError as e:
        return {"status": "error", "message": str(e)}
