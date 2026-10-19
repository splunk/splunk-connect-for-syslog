from app import mcp, REPO_ROOT
from utils.http import sc4s_request


CONTEXT_TEMPLATES = REPO_ROOT / "package" / "etc" / "context_templates"


# ---------------------------------------------------------------------------
# splunk_metadata.csv
# ---------------------------------------------------------------------------


@mcp.tool
def get_splunk_metadata() -> dict:
    """Read Splunk metadata overrides from the running SC4S instance.

    Returns:
        Dict with entries (key, metadata, value rows), or status=error and details.
    """
    return sc4s_request("get", "/config/metadata/splunk", timeout=30)


@mcp.tool
def set_splunk_metadata(entries: list[dict]) -> dict:
    """Replace all Splunk metadata overrides and restart SC4S asynchronously.

    Args:
        entries: Complete list of key (vendor_product), metadata and value rows.
            metadata: index, source, sourcetype, host or sc4s_template.

    Returns:
        Dict with job_id to poll via get_job_status, or status=error and details.
    """
    return sc4s_request(
        "post",
        "/config/metadata/splunk",
        json={"entries": entries},
        timeout=30,
    )


@mcp.tool
def delete_splunk_metadata() -> dict:
    """Clear all Splunk metadata overrides and restart SC4S asynchronously.

    Returns:
        Dict with job_id to poll via get_job_status, or status=error and details.
    """
    return sc4s_request("delete", "/config/metadata/splunk", timeout=30)


# ---------------------------------------------------------------------------
# compliance_meta_by_source (.conf + .csv)
# ---------------------------------------------------------------------------


@mcp.tool
def get_compliance_overrides() -> dict:
    """Read compliance metadata overrides from the running SC4S instance.

    Returns:
        Dict with conf_content (filters) and csv_content (filter_name, field_name,
        value rows), or status=error and details.
    """
    return sc4s_request("get", "/config/metadata/compliance", timeout=10)


@mcp.tool
def set_compliance_override(conf_content: str, csv_content: list[dict]) -> dict:
    """Replace both compliance override files and restart SC4S asynchronously.

    Args:
        conf_content: Complete syslog-ng filter definitions.
        csv_content: Complete list of filter_name, field_name and value rows.
            Fields: .splunk.index, .splunk.source, .splunk.sourcetype or fields.<name>.

    Returns:
        Dict with job_id to poll via get_job_status, or status=error and details.
    """
    return sc4s_request(
        "post",
        "/config/metadata/compliance",
        json={"conf_content": conf_content, "csv_content": csv_content},
        timeout=30,
    )


@mcp.tool
def delete_compliance_override() -> dict:
    """Clear both compliance override files and restart SC4S asynchronously.

    Returns:
        Dict with job_id to poll via get_job_status, or status=error and details.
    """
    return sc4s_request("delete", "/config/metadata/compliance", timeout=30)
