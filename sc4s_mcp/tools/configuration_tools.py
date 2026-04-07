import os
import re

import httpx

from app import mcp, REPO_ROOT

SC4S_API_URL = os.getenv("SC4S_API_URL", "http://localhost:8080")


def _sc4s_request(method: str, path: str, **kwargs) -> dict:
    """Execute an HTTP request against the SC4S API with unified error handling."""
    url = f"{SC4S_API_URL}{path}"
    try:
        resp = getattr(httpx, method)(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        return {"status": "error", "message": f"SC4S instance unreachable at {SC4S_API_URL}"}
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


@mcp.tool
def list_vendors() -> list[str]:
    """Lists all vendors supported by SC4S, based on the directories from known sources page in docs."""
    sources_vendor_dir = REPO_ROOT / "docs" / "sources" / "vendor"
    return [d.name for d in sources_vendor_dir.iterdir() if d.is_dir()]


@mcp.tool
def list_all_parsers() -> list[str]:
    """Lists all parsers, based on the .conf files in addon directory."""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    return [str(f.relative_to(REPO_ROOT)) for f in addons_dir.rglob("*.conf")]


@mcp.tool
def list_vendor_parsers(vendor: str) -> list[str]:
    """Lists parsers for given vendor, based on the parsers in addon directory."""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    results = []
    vendor_pattern = re.compile(rf"\b{re.escape(vendor)}\b", re.IGNORECASE)

    for conf_file in addons_dir.rglob("*.conf"):
        try:
            content = conf_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if vendor_pattern.search(content):
            results.append(str(conf_file.relative_to(REPO_ROOT)))

    return results


@mcp.tool
def get_parser(parser_name: str) -> dict:
    """Get parser content by filename from addon library. Returns a dict with 'found', 'path', and 'content' keys."""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    for conf_file in addons_dir.rglob("*.conf"):
        if conf_file.name == parser_name or conf_file.stem == parser_name:
            return {
                "found": True,
                "path": str(conf_file.relative_to(REPO_ROOT)),
                "content": conf_file.read_text(encoding="utf-8"),
            }
    return {"found": False, "message": f"Parser '{parser_name}' not found"}


@mcp.tool
def search_docs(query: str) -> list[str]:
    """Full text search for a pattern in the documentation files within docs/. Returns matching lines with filename and line number."""
    docs_dir = REPO_ROOT / "docs"
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except re.error as e:
        return [f"Invalid regex '{query}': {e}"]

    results = []
    for doc_file in docs_dir.rglob("*.md"):
        try:
            lines = doc_file.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for idx, line in enumerate(lines):
            if pattern.search(line):
                results.append(f"{doc_file.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
    return results


@mcp.tool
def sc4s_health() -> dict:
    """Check the health status of a running SC4S instance."""
    return _sc4s_request("get", "/health", timeout=10)


@mcp.tool
def sc4s_set_env(env_file_content: str) -> dict:
    """Upload a new env_file to the running SC4S instance. Provide the full env_file content as a string. SC4S will backup the current env_file, apply the new one, and restart syslog-ng."""
    return _sc4s_request(
        "post",
        "/config/env",
        files={"file": ("env_file", env_file_content.encode("utf-8"))},
        timeout=30,
    )


@mcp.tool
def sc4s_get_env() -> dict:
    """Read the current env_file from the running SC4S instance."""
    return _sc4s_request("get", "/config/env", timeout=10)


@mcp.tool
def sc4s_add_parser(filename: str, content: str) -> dict:
    """Upload a new parser .conf file to the running SC4S instance. SC4S will validate the syntax and restart syslog-ng. If syntax check fails, the parser is rolled back."""
    if not filename.endswith(".conf"):
        filename += ".conf"
    return _sc4s_request(
        "post",
        "/config/parser",
        files={"file": (filename, content.encode("utf-8"))},
        timeout=30,
    )


@mcp.tool
def sc4s_delete_parser(name: str) -> dict:
    """Delete a custom parser from the running SC4S instance. SC4S will validate the config after removal and restart syslog-ng. If validation fails, the parser is restored."""
    return _sc4s_request("delete", f"/config/parser/{name}", timeout=30)


@mcp.tool
def sc4s_list_custom_parsers() -> dict:
    """List all custom parsers currently deployed on the running SC4S instance."""
    return _sc4s_request("get", "/config/parsers", timeout=10)


@mcp.tool
def sc4s_get_custom_parser(name: str) -> dict:
    """Read the content of a custom parser deployed on the running SC4S instance."""
    return _sc4s_request("get", f"/config/parser/{name}", timeout=10)
