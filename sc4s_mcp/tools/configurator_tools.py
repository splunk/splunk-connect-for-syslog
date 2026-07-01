import re
import subprocess
from pathlib import Path

from app import mcp

# configuration-tool.sh lives at the repo root, three levels above this file:
#   sc4s_mcp/tools/configurator_tools.py  ->  ../../..  ->  repo root
_SCRIPT_PATH = Path(__file__).resolve().parent.parent.parent / "configuration-tool.sh"

_HEC_URL_RE = re.compile(r"^https?://")
_HEC_TOKEN_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@mcp.tool
def sc4s_build_config(
    hec_url: str,
    hec_token: str,
    tls_verify: str = "yes",
    protocol: str = "both",
    mode: str = "custom",
    hardware: str = "",
    expected_eps: int = 1000,
    default_timezone: str = "",
    source_udp_fetch_limit: int = 0,
    source_listen_udp_sockets: int = 0,
    source_udp_so_rcvbuff: int = 0,
    enable_ebpf: str = "",
    ebpf_no_sockets: int = 0,
    source_udp_iw_use: str = "",
    source_udp_iw_size: int = 0,
    source_tcp_so_rcvbuff: int = 0,
    enable_parallelize: str = "",
    parallelize_no_partition: int = 0,
    source_tcp_iw_use: str = "",
    source_tcp_iw_size: int = 0,
    diskbuff_enable: str = "",
    diskbuff_reliable: str = "",
    diskbuff_membufsize: int = 0,
    diskbuff_diskbufsize: int = 0,
) -> str:
    """Generates a new SC4S env_file from scratch by running the configuration script
    with the provided parameters. Use this when setting up SC4S for the first time
    or creating a new configuration file.

    Args:
        hec_url: Splunk HEC URL, e.g. https://splunk.example.com:8088 (required).
        hec_token: Splunk HEC token in UUID format, e.g. 12345678-1234-1234-1234-123456789abc (required).
        tls_verify: Verify SSL/TLS certificates — yes or no (default: yes).
        protocol: Protocol optimisation — udp, tcp, or both (default: both).
        mode: Configuration mode — custom or hardware (default: custom).
        hardware: Hardware profile for hardware mode — 4vCPUs, 8vCPUs, or 16vCPUs.
        expected_eps: Expected events per second (default: 1000).
        default_timezone: Optional default timezone in Region/City format, e.g. America/New_York.
        source_udp_fetch_limit: SC4S_SOURCE_UDP_FETCH_LIMIT override (0 = use script default).
        source_listen_udp_sockets: SC4S_SOURCE_LISTEN_UDP_SOCKETS override (0 = use script default).
        source_udp_so_rcvbuff: SC4S_SOURCE_UDP_SO_RCVBUFF override (0 = use script default).
        enable_ebpf: SC4S_ENABLE_EBPF override — yes or no.
        ebpf_no_sockets: SC4S_EBPF_NO_SOCKETS override (0 = use script default).
        source_udp_iw_use: SC4S_SOURCE_UDP_IW_USE override — yes or no.
        source_udp_iw_size: SC4S_SOURCE_UDP_IW_SIZE override (0 = use script default).
        source_tcp_so_rcvbuff: SC4S_SOURCE_TCP_SO_RCVBUFF override (0 = use script default).
        enable_parallelize: SC4S_ENABLE_PARALLELIZE override — yes or no.
        parallelize_no_partition: SC4S_PARALLELIZE_NO_PARTITION override (0 = use script default).
        source_tcp_iw_use: SC4S_SOURCE_TCP_IW_USE override — yes or no.
        source_tcp_iw_size: SC4S_SOURCE_TCP_IW_SIZE override (0 = use script default).
        diskbuff_enable: SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE override — yes or no.
        diskbuff_reliable: SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE override — yes or no.
        diskbuff_membufsize: SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE override (0 = use script default).
        diskbuff_diskbufsize: SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE override (0 = use script default).

    Returns:
        The generated env_file content as a string, or an error message prefixed with 'Error:'.
    """
    # --- Validate required parameters before touching subprocess ---
    if not _HEC_URL_RE.match(hec_url):
        return (
            f"Error: hec_url '{hec_url}' is not valid. "
            "It must start with http:// or https://."
        )

    if not _HEC_TOKEN_RE.match(hec_token):
        return (
            f"Error: hec_token '{hec_token}' is not a valid UUID. "
            "Expected format: 12345678-1234-1234-1234-123456789abc."
        )

    # --- Build environment for the subprocess ---
    env: dict[str, str] = {
        "SC4S_NON_INTERACTIVE": "1",
        "SC4S_HEC_URL": hec_url,
        "SC4S_HEC_TOKEN": hec_token,
        "SC4S_TLS_VERIFY": tls_verify,
        "SC4S_PROTOCOL": protocol,
        "SC4S_MODE": mode,
        "SC4S_EXPECTED_EPS": str(expected_eps),
        # PATH is needed so the script can invoke standard utilities
        "PATH": "/usr/local/bin:/usr/bin:/bin",
    }

    if hardware:
        env["SC4S_HARDWARE"] = hardware

    if default_timezone:
        env["SC4S_DEFAULT_TIMEZONE"] = default_timezone

    # Optional tuning overrides — only set when caller provided a non-zero / non-empty value
    _int_overrides: list[tuple[str, int]] = [
        ("SC4S_SOURCE_UDP_FETCH_LIMIT", source_udp_fetch_limit),
        ("SC4S_SOURCE_LISTEN_UDP_SOCKETS", source_listen_udp_sockets),
        ("SC4S_SOURCE_UDP_SO_RCVBUFF", source_udp_so_rcvbuff),
        ("SC4S_EBPF_NO_SOCKETS", ebpf_no_sockets),
        ("SC4S_SOURCE_UDP_IW_SIZE", source_udp_iw_size),
        ("SC4S_SOURCE_TCP_SO_RCVBUFF", source_tcp_so_rcvbuff),
        ("SC4S_PARALLELIZE_NO_PARTITION", parallelize_no_partition),
        ("SC4S_SOURCE_TCP_IW_SIZE", source_tcp_iw_size),
        ("SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE", diskbuff_membufsize),
        ("SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE", diskbuff_diskbufsize),
    ]
    for key, value in _int_overrides:
        if value != 0:
            env[key] = str(value)

    _str_overrides: list[tuple[str, str]] = [
        ("SC4S_ENABLE_EBPF", enable_ebpf),
        ("SC4S_SOURCE_UDP_IW_USE", source_udp_iw_use),
        ("SC4S_ENABLE_PARALLELIZE", enable_parallelize),
        ("SC4S_SOURCE_TCP_IW_USE", source_tcp_iw_use),
        ("SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE", diskbuff_enable),
        ("SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE", diskbuff_reliable),
    ]
    for key, value in _str_overrides:
        if value:
            env[key] = value

    # --- Execute the script ---
    try:
        result = subprocess.run(
            ["/bin/bash", str(_SCRIPT_PATH)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return f"Error: configuration-tool.sh not found at {_SCRIPT_PATH}."
    except subprocess.TimeoutExpired:
        return "Error: configuration-tool.sh timed out after 30 seconds."
    except Exception as exc:  # noqa: BLE001
        return f"Error: unexpected error running configuration-tool.sh: {exc}"

    if result.returncode != 0:
        stderr = result.stderr.strip()
        return f"Error: configuration-tool.sh exited with code {result.returncode}. {stderr}"

    return result.stdout
