"""Tests for script-backed SC4S configuration generation."""

import subprocess
from unittest.mock import MagicMock, patch

from tools.configuration_tools import sc4s_build_config


URL = "https://splunk.example.com:8088"
TOKEN = "12345678-1234-1234-1234-123456789abc"


def completed(stdout="CONFIG\n", stderr="", returncode=0):
    result = MagicMock(spec=subprocess.CompletedProcess)
    result.stdout = stdout
    result.stderr = stderr
    result.returncode = returncode
    return result


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_returns_exact_script_stdout(mock_run):
    mock_run.return_value = completed(stdout="A=1\n\n")
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        result = sc4s_build_config(URL, TOKEN)

    assert result == {"config": "A=1\n\n", "warnings": []}
    assert mock_run.call_args.args[0] == ["bash", "/app/configuration-tool.sh"]
    assert mock_run.call_args.kwargs["timeout"] == 30


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_translates_all_custom_inputs(mock_run):
    mock_run.return_value = completed()
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        sc4s_build_config(
            URL,
            TOKEN,
            protocol="udp",
            adjust_fetch_limit=True,
            udp_fetch_limit=5000,
            adjust_listen_sockets=True,
            udp_listen_sockets=7,
            udp_receive_buffer=1000,
            ebpf_enabled=True,
            ebpf_sockets=6,
            udp_input_window_enabled=True,
            udp_input_window_size=2000,
            tcp_receive_buffer=3000,
            parallelize_enabled=True,
            parallelize_partitions=3,
            tcp_input_window_enabled=True,
            tcp_input_window_size=4000,
            adjust_disk_buffer=True,
            disk_buffer_enabled=True,
            disk_buffer_reliable=True,
            disk_buffer_memory_size=1000,
            disk_buffer_size=2000,
            timezone="Europe/Warsaw",
        )

    env = mock_run.call_args.kwargs["env"]
    assert env["SC4S_NON_INTERACTIVE"] == "1"
    assert env["SC4S_MODE"] == "1"
    assert env["SC4S_PROTOCOL"] == "udp"
    assert env["SC4S_ADJUST_FETCH_LIMIT"] == "yes"
    assert env["SC4S_SOURCE_UDP_FETCH_LIMIT"] == "5000"
    assert env["SC4S_ADJUST_LISTEN_SOCKETS"] == "yes"
    assert env["SC4S_SOURCE_LISTEN_UDP_SOCKETS"] == "7"
    assert env["SC4S_SOURCE_UDP_SO_RCVBUFF"] == "1000"
    assert env["SC4S_ENABLE_EBPF"] == "yes"
    assert env["SC4S_EBPF_NO_SOCKETS"] == "6"
    assert env["SC4S_SOURCE_UDP_IW_USE"] == "yes"
    assert env["SC4S_SOURCE_UDP_IW_SIZE"] == "2000"
    assert env["SC4S_SOURCE_TCP_SO_RCVBUFF"] == "3000"
    assert env["SC4S_PARALLELIZE"] == "yes"
    assert env["SC4S_PARALLELIZE_NO_PARTITION"] == "3"
    assert env["SC4S_SOURCE_TCP_IW_USE"] == "yes"
    assert env["SC4S_SOURCE_TCP_IW_SIZE"] == "4000"
    assert env["SC4S_ADJUST_DISKBUFF"] == "yes"
    assert env["SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE"] == "yes"
    assert env["SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE"] == "yes"
    assert env["SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE"] == "1000"
    assert env["SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE"] == "2000"
    assert env["SC4S_DEFAULT_TIMEZONE"] == "Europe/Warsaw"


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_hardware_inputs_are_owned_by_script(mock_run):
    mock_run.return_value = completed()
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        sc4s_build_config(
            URL,
            TOKEN,
            mode="hardware",
            hardware_profile="4vCPUs",
            expected_eps=25001,
        )

    env = mock_run.call_args.kwargs["env"]
    assert env["SC4S_MODE"] == "2"
    assert env["SC4S_HARDWARE"] == "4vCPUs"
    assert env["SC4S_EXPECTED_EPS"] == "25001"


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_removes_ambient_sc4s_variables(mock_run, monkeypatch):
    monkeypatch.setenv("SC4S_UNRELATED_AMBIENT_VALUE", "must-not-leak")
    mock_run.return_value = completed()
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        sc4s_build_config(URL, TOKEN)

    assert "SC4S_UNRELATED_AMBIENT_VALUE" not in mock_run.call_args.kwargs["env"]


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_surfaces_script_failure(mock_run):
    mock_run.return_value = completed(
        stderr="Error: invalid SC4S_PROTOCOL\n", returncode=1
    )
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        result = sc4s_build_config(URL, TOKEN)

    assert result == {
        "error": "Configuration script failed (exit 1): Error: invalid SC4S_PROTOCOL"
    }


@patch(
    "tools.configuration_tools.subprocess.run",
    side_effect=subprocess.TimeoutExpired("bash", 30),
)
def test_build_config_surfaces_timeout(_mock_run):
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True

        result = sc4s_build_config(URL, TOKEN)

    assert result == {"error": "Configuration script timed out after 30 seconds."}


@patch("tools.configuration_tools.subprocess.run", side_effect=OSError("no bash"))
def test_build_config_surfaces_launch_error(_mock_run):
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True

        result = sc4s_build_config(URL, TOKEN)

    assert result == {"error": "Failed to run configuration script: no bash"}


def test_build_config_surfaces_missing_script():
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = False
        script.__str__ = lambda _: "/missing/configuration-tool.sh"

        result = sc4s_build_config(URL, TOKEN)

    assert result == {
        "error": "Configuration script not found at /missing/configuration-tool.sh"
    }


@patch("tools.configuration_tools.subprocess.run")
def test_build_config_surfaces_script_and_security_warnings(mock_run):
    mock_run.return_value = completed(stderr="script warning\n")
    with patch("tools.configuration_tools._CONFIG_SCRIPT") as script:
        script.exists.return_value = True
        script.__str__ = lambda _: "/app/configuration-tool.sh"

        result = sc4s_build_config(
            "http://splunk.example.com:8088",
            TOKEN,
            tls_verify=False,
        )

    assert result["warnings"][0] == "script warning"
    assert any("TLS verification" in warning for warning in result["warnings"])
    assert any("plaintext HTTP" in warning for warning in result["warnings"])


def test_build_config_executes_repository_script():
    result = sc4s_build_config(URL, TOKEN)

    assert "error" not in result
    assert f"SC4S_DEST_SPLUNK_HEC_DEFAULT_URL={URL}" in result["config"]
    assert f"SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN={TOKEN}" in result["config"]
