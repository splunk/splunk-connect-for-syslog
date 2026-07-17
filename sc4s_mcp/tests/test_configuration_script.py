import os
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "configuration-tool.sh"
TOKEN = "12345678-1234-1234-1234-123456789abc"


def run_script(**overrides: str) -> subprocess.CompletedProcess[str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("SC4S_")
    }
    env.update(
        {
            "SC4S_NON_INTERACTIVE": "1",
            "SC4S_HEC_URL": "https://splunk.example.com:8088",
            "SC4S_HEC_TOKEN": TOKEN,
        }
    )
    env.update(overrides)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_non_interactive_default_config_is_stdout_only():
    result = run_script()

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert (
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://splunk.example.com:8088"
        in result.stdout
    )
    assert f"SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN={TOKEN}" in result.stdout
    assert "Review Configuration" not in result.stdout
    assert "Configuration saved successfully" not in result.stdout


def test_non_interactive_custom_tuning_uses_existing_renderer():
    result = run_script(
        SC4S_MODE="1",
        SC4S_PROTOCOL="both",
        SC4S_ADJUST_FETCH_LIMIT="yes",
        SC4S_SOURCE_UDP_FETCH_LIMIT="5000",
        SC4S_ENABLE_EBPF="yes",
        SC4S_EBPF_NO_SOCKETS="6",
        SC4S_PARALLELIZE="yes",
        SC4S_PARALLELIZE_NO_PARTITION="3",
        SC4S_ADJUST_DISKBUFF="yes",
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE="yes",
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE="yes",
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE="1000",
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE="2000",
        SC4S_DEFAULT_TIMEZONE="Europe/Warsaw",
    )

    assert result.returncode == 0
    for line in (
        "SC4S_SOURCE_UDP_FETCH_LIMIT=5000",
        "SC4S_ENABLE_EBPF=yes",
        "SC4S_EBPF_NO_SOCKETS=6",
        "SC4S_ENABLE_PARALLELIZE=yes",
        "SC4S_PARALLELIZE_NO_PARTITION=3",
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=1000",
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=2000",
        "SC4S_DEFAULT_TIMEZONE=Europe/Warsaw",
    ):
        assert line in result.stdout


def test_non_interactive_hardware_mode_runs_script_threshold_logic():
    result = run_script(
        SC4S_MODE="2",
        SC4S_HARDWARE="4vCPUs",
        SC4S_PROTOCOL="both",
        SC4S_EXPECTED_EPS="25001",
    )

    assert result.returncode == 0
    assert "# Mode: Hardware-based (4vCPUs)" in result.stdout
    assert "SC4S_SOURCE_UDP_FETCH_LIMIT=1000000" in result.stdout
    assert "SC4S_ENABLE_PARALLELIZE=yes" in result.stdout
    assert "SC4S_PARALLELIZE_NO_PARTITION=4" in result.stdout


def test_non_interactive_invalid_input_fails_without_config():
    result = run_script(SC4S_HEC_URL="not-a-url")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "SC4S_HEC_URL" in result.stderr


def test_non_interactive_rejects_multiline_hec_url():
    result = run_script(
        SC4S_HEC_URL="https://splunk.example.com:8088/\nINJECTED=yes"
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "SC4S_HEC_URL" in result.stderr


def test_non_interactive_rejects_invalid_boolean():
    result = run_script(SC4S_ENABLE_EBPF="maybe")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "SC4S_ENABLE_EBPF" in result.stderr


def test_non_interactive_rejects_invalid_integer():
    result = run_script(
        SC4S_ENABLE_EBPF="yes",
        SC4S_EBPF_NO_SOCKETS="many",
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "SC4S_EBPF_NO_SOCKETS" in result.stderr


def test_help_documents_non_interactive_contract():
    result = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "SC4S_NON_INTERACTIVE=1" in result.stdout
    assert "SC4S_HEC_URL" in result.stdout
    assert "SC4S_HEC_TOKEN" in result.stdout


def test_interactive_mode_still_shows_banner_and_validates_mode():
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        input="3\n",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode != 0
    assert "SC4S Configuration Tool" in result.stdout
    assert "Choose configuration mode" in result.stdout
    assert "Invalid mode selection" in result.stdout
