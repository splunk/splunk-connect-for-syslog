from app import mcp, REPO_ROOT
from utils.http import sc4s_request


CONTEXT_TEMPLATES = REPO_ROOT / "package" / "etc" / "context_templates"


# ---------------------------------------------------------------------------
# splunk_metadata.csv
# ---------------------------------------------------------------------------


@mcp.tool
def sc4s_set_splunk_metadata(entries: list[dict]) -> dict:
    """Overwrite the splunk_metadata.csv on the running SC4S instance. Restarts SC4S.
    Example: [{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}]"""
    return sc4s_request(
        "post",
        "/config/metadata/splunk",
        json={"entries": entries},
        timeout=30,
    )


@mcp.tool
def sc4s_delete_splunk_metadata() -> dict:
    """Clear the splunk_metadata.csv on the running SC4S instance. SC4S restarts after clearing."""
    return sc4s_request("delete", "/config/metadata/splunk", timeout=30)
