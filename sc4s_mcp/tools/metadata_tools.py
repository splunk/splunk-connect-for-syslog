from app import mcp, REPO_ROOT
from utils.http import sc4s_request


CONTEXT_TEMPLATES = REPO_ROOT / "package" / "etc" / "context_templates"


# ---------------------------------------------------------------------------
# splunk_metadata.csv
# ---------------------------------------------------------------------------

@mcp.tool
def sc4s_get_splunk_metadata() -> dict:
    """Read all current Splunk metadata overrides from the running SC4S instance.
    Returns entries from splunk_metadata.csv with key, metadata, and value columns.
    The 'key' is a vendor_product identifier, 'metadata' is one of: index, source,
    sourcetype, host, sc4s_template."""
    return sc4s_request("get", "/config/metadata/splunk", timeout=10)


@mcp.tool
def sc4s_set_splunk_metadata(entries: list[dict]) -> dict:
    """Overwrite the entire splunk_metadata.csv on the running SC4S instance.
    The provided entries completely replace the file contents. Each entry must have
    'key' (vendor_product), 'metadata' (index/source/sourcetype/host/sc4s_template),
    and 'value'. SC4S restarts after applying changes. Call sc4s_get_splunk_metadata
    first if you need to preserve existing entries.

    Example: [{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}]"""
    return sc4s_request(
        "post", "/config/metadata/splunk", json={"entries": entries}, timeout=30,
    )


@mcp.tool
def sc4s_delete_splunk_metadata() -> dict:
    """Clear the entire splunk_metadata.csv on the running SC4S instance,
    removing all metadata overrides. SC4S restarts after clearing."""
    return sc4s_request("delete", "/config/metadata/splunk", timeout=30)