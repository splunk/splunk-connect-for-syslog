import os
import re
import subprocess
from pathlib import Path
from typing import Literal

from app import mcp, REPO_ROOT
from utils.http import sc4s_request as _sc4s_request


SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "parser-creator"
_CONFIG_SCRIPT: Path = REPO_ROOT / "configuration-tool.sh"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


@mcp.tool
def sc4s_build_config(
    hec_url: str,
    hec_token: str,
    tls_verify: bool = True,
    protocol: Literal["udp", "tcp", "both"] = "both",
    mode: Literal["custom", "hardware"] = "custom",
    hardware_profile: str = "8vCPUs",
    expected_eps: int = 1000,
    timezone: str = "",
    adjust_fetch_limit: bool = False,
    udp_fetch_limit: int = 1000,
    adjust_listen_sockets: bool = False,
    udp_listen_sockets: int = 2,
    udp_receive_buffer: int = -1,
    ebpf_enabled: bool = False,
    ebpf_sockets: int = 4,
    udp_input_window_enabled: bool = False,
    udp_input_window_size: int = 250000,
    tcp_receive_buffer: int = -1,
    parallelize_enabled: bool = False,
    parallelize_partitions: int = 4,
    tcp_input_window_enabled: bool = False,
    tcp_input_window_size: int = 20000000,
    adjust_disk_buffer: bool = False,
    disk_buffer_enabled: bool = True,
    disk_buffer_reliable: bool = False,
    disk_buffer_memory_size: int = 163840000,
    disk_buffer_size: int = 53687091200,
) -> dict:
    """Generate an env_file by executing the actual configuration-tool.sh.

    This tool only generates content. It does not modify a running SC4S
    instance; live changes require the separate get_env and set_env tools.
    """
    if not _CONFIG_SCRIPT.exists():
        return {"error": f"Configuration script not found at {_CONFIG_SCRIPT}"}

    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("SC4S_")
    }
    env.update(
        {
            "SC4S_NON_INTERACTIVE": "1",
            "SC4S_HEC_URL": hec_url,
            "SC4S_HEC_TOKEN": hec_token,
            "SC4S_TLS_VERIFY": _yes_no(tls_verify),
            "SC4S_PROTOCOL": protocol,
            "SC4S_MODE": "2" if mode == "hardware" else "1",
            "SC4S_HARDWARE": hardware_profile,
            "SC4S_EXPECTED_EPS": str(expected_eps),
            "SC4S_DEFAULT_TIMEZONE": timezone,
            "SC4S_ADJUST_FETCH_LIMIT": _yes_no(adjust_fetch_limit),
            "SC4S_SOURCE_UDP_FETCH_LIMIT": str(udp_fetch_limit),
            "SC4S_ADJUST_LISTEN_SOCKETS": _yes_no(adjust_listen_sockets),
            "SC4S_SOURCE_LISTEN_UDP_SOCKETS": str(udp_listen_sockets),
            "SC4S_SOURCE_UDP_SO_RCVBUFF": str(udp_receive_buffer),
            "SC4S_ENABLE_EBPF": _yes_no(ebpf_enabled),
            "SC4S_EBPF_NO_SOCKETS": str(ebpf_sockets),
            "SC4S_SOURCE_UDP_IW_USE": _yes_no(udp_input_window_enabled),
            "SC4S_SOURCE_UDP_IW_SIZE": str(udp_input_window_size),
            "SC4S_SOURCE_TCP_SO_RCVBUFF": str(tcp_receive_buffer),
            "SC4S_PARALLELIZE": _yes_no(parallelize_enabled),
            "SC4S_PARALLELIZE_NO_PARTITION": str(parallelize_partitions),
            "SC4S_SOURCE_TCP_IW_USE": _yes_no(tcp_input_window_enabled),
            "SC4S_SOURCE_TCP_IW_SIZE": str(tcp_input_window_size),
            "SC4S_ADJUST_DISKBUFF": _yes_no(adjust_disk_buffer),
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE": _yes_no(
                disk_buffer_enabled
            ),
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE": _yes_no(
                disk_buffer_reliable
            ),
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE": str(
                disk_buffer_memory_size
            ),
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE": str(
                disk_buffer_size
            ),
        }
    )

    try:
        result = subprocess.run(
            ["bash", str(_CONFIG_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": "Configuration script timed out after 30 seconds."}
    except OSError as exc:
        return {"error": f"Failed to run configuration script: {exc}"}

    if result.returncode != 0:
        detail = result.stderr.strip()
        suffix = f": {detail}" if detail else ""
        return {
            "error": f"Configuration script failed (exit {result.returncode}){suffix}"
        }

    warnings = []
    if result.stderr.strip():
        warnings.append(result.stderr.strip())
    if not tls_verify:
        warnings.append(
            "TLS verification is disabled; use this only for development or "
            "trusted self-signed certificates."
        )
    if hec_url.startswith("http://"):
        warnings.append(
            "The HEC URL uses plaintext HTTP; the token and log data will be "
            "unencrypted."
        )

    return {"config": result.stdout, "warnings": warnings}


@mcp.tool
def get_parser_creation_guide() -> str:
    """Get the complete SC4S parser creation guide. Call this tool BEFORE creating
    a new parser when the user asks to create a parser, add support for a new log
    source, or add a new vendor. Returns syntax reference, filter topics, rewrite
    functions, examples, and a completion checklist."""
    sections = []
    for path in [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "references" / "testing-parsers.md",
    ]:
        if path.exists():
            sections.append(path.read_text(encoding="utf-8"))
    return (
        "\n\n---\n\n".join(sections) if sections else "Parser creation guide not found"
    )


@mcp.tool
def list_vendors() -> list[str]:
    """Lists all vendors supported by SC4S, based on the directories from known sources page in docs."""
    sources_vendor_dir = REPO_ROOT / "docs" / "sources" / "vendor"
    return [d.name for d in sources_vendor_dir.iterdir() if d.is_dir()]


@mcp.tool
def list_all_parsers() -> list[str]:
    """Lists all parsers, based on the .conf files in addon directory."""
    addons_dir = REPO_ROOT / "package" / "shared" / "addons"
    return [str(f.relative_to(REPO_ROOT)) for f in addons_dir.rglob("*.conf")]


@mcp.tool
def list_vendor_parsers(vendor: str) -> list[str]:
    """Lists parsers for given vendor, based on the parsers in addon directory."""
    addons_dir = REPO_ROOT / "package" / "shared" / "addons"
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
    addons_dir = REPO_ROOT / "package" / "shared" / "addons"
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
                results.append(
                    f"{doc_file.relative_to(REPO_ROOT)}:{idx}: {line.strip()}"
                )
    return results


@mcp.tool
def sc4s_health() -> dict:
    """Check the health status of a running SC4S instance."""
    return _sc4s_request("get", "/health", timeout=10)


@mcp.tool
def get_job_status(job_id: str) -> dict:
    """Get the current state and result of an asynchronous configuration job."""
    return _sc4s_request("get", f"/jobs/{job_id}", timeout=10)


@mcp.tool
def set_env(env_file_content: str) -> dict:
    """Upload an env_file and return a job ID for polling with get_job_status."""
    return _sc4s_request(
        "post",
        "/config/env",
        files={"file": ("env_file", env_file_content.encode("utf-8"))},
        timeout=30,
    )


@mcp.tool
def get_env() -> dict:
    """Read the current env_file from the running SC4S instance."""
    return _sc4s_request("get", "/config/env", timeout=10)


@mcp.tool
def add_parser(filename: str, content: str) -> dict:
    """Upload a parser and return a job ID for polling with get_job_status."""
    if not filename.endswith(".conf"):
        filename += ".conf"
    return _sc4s_request(
        "post",
        "/config/parser",
        files={"file": (filename, content.encode("utf-8"))},
        timeout=30,
    )


@mcp.tool
def delete_parser(name: str) -> dict:
    """Delete a parser and return a job ID for polling with get_job_status."""
    return _sc4s_request("delete", f"/config/parser/{name}", timeout=30)


@mcp.tool
def list_custom_parsers() -> dict:
    """List all custom parsers currently deployed on the running SC4S instance."""
    return _sc4s_request("get", "/config/parsers", timeout=10)


@mcp.tool
def get_custom_parser(name: str) -> dict:
    """Read the content of a custom parser deployed on the running SC4S instance."""
    return _sc4s_request("get", f"/config/parser/{name}", timeout=10)
