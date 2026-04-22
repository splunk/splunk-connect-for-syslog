from app import mcp, REPO_ROOT
from utils.http import sc4s_request


CONTEXT_TEMPLATES = REPO_ROOT / "package" / "etc" / "context_templates"


# ---------------------------------------------------------------------------
# splunk_metadata.csv
# ---------------------------------------------------------------------------


@mcp.tool
def sc4s_get_splunk_metadata() -> dict:
    """Read Splunk metadata overrides from the running SC4S instance.
    Returns entries from splunk_metadata.csv with key, metadata, and value columns.
    The 'key' is a vendor_product identifier, 'metadata' is one of: index, source,
    sourcetype, host, sc4s_template."""
    return sc4s_request("get", "/config/metadata/splunk", timeout=30)


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


# ---------------------------------------------------------------------------
# compliance_meta_by_source (.conf + .csv)
# ---------------------------------------------------------------------------


@mcp.tool
def sc4s_get_compliance_overrides() -> dict:
    """Read compliance metadata overrides from the running SC4S instance.
    Returns the syslog-ng filter definitions (conf_content) and CSV rows (csv_content)
    with filter_name, field_name, and value. These overrides redirect events to different
    Splunk indexes or add indexed fields based on host, IP, or subnet matching."""
    return sc4s_request("get", "/config/metadata/compliance", timeout=10)


@mcp.tool
def sc4s_set_compliance_override(conf_content: str, csv_content: list[dict]) -> dict:
    """Overwrite the compliance_meta_by_source conf and CSV files instance.
    The provided content completely replaces both files. SC4S restarts after applying changes.

    Args:
        conf_content: Complete syslog-ng filter definitions, e.g.:
            'filter f_pci_zone { host("pci-*" type(glob)) or netmask(10.1.0.0/16) };'
        csv_content: List of dicts with 'filter_name', 'field_name', 'value'. Field names
            must be .splunk.index, .splunk.source, .splunk.sourcetype, or fields.<name>.
            Example: [{"filter_name": "f_pci_zone", "field_name": ".splunk.index", "value": "pci_idx"}]
    """
    return sc4s_request(
        "post",
        "/config/metadata/compliance",
        json={"conf_content": conf_content, "csv_content": csv_content},
        timeout=30,
    )


@mcp.tool
def sc4s_delete_compliance_override() -> dict:
    """Clear both compliance_meta_by_source files (conf and CSV), removing all compliance overrides. SC4S restarts after clearing."""
    return sc4s_request("delete", "/config/metadata/compliance", timeout=30)
