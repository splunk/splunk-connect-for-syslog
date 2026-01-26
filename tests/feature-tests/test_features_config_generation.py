"""
Tests for SC4S feature configuration generation.

These tests verify that plugin.py correctly generates syslog-ng configuration
for various SC4S features (eBPF, parallelize, etc.) based on environment variables.
"""

import os
import subprocess
import sys

import pytest

def run_plugin(env_vars: dict) -> subprocess.CompletedProcess:
    env = env_vars.copy()

    env.setdefault("SOURCE_ALL_SET", "DEFAULT")
    env.setdefault("SC4S_LISTEN_DEFAULT_UDP_PORT", "514")
    env.setdefault("SC4S_LISTEN_DEFAULT_TCP_PORT", "514")

    plugin_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..",
        "package", "etc", "conf.d", "sources", "source_syslog", "plugin.py"
    )

    result = subprocess.run(
        [sys.executable, plugin_path],
        capture_output=True,
        text=True,
        env=env,
        cwd=os.path.dirname(plugin_path)
    )

    return result


def run_dest_hec_plugin(env_vars: dict) -> subprocess.CompletedProcess:
    """Run the dest_hec plugin.py to generate HEC destination configuration."""
    env = env_vars.copy()

    # Required defaults for HEC destination
    env.setdefault("SC4S_DEST_SPLUNK_HEC_DEFAULT_URL", "https://splunk:8088")
    env.setdefault("SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN", "test-token")

    plugin_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..",
        "package", "etc", "conf.d", "destinations", "dest_hec", "plugin.py"
    )

    result = subprocess.run(
        [sys.executable, plugin_path],
        capture_output=True,
        text=True,
        env=env,
        cwd=os.path.dirname(plugin_path)
    )

    return result


# =============================================================================
# Ebpf Tests
# =============================================================================

@pytest.mark.features("ebpf")
def test_ebpf_config_generation():
    result = run_plugin({
        "SC4S_ENABLE_EBPF": "yes",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "ebpf(reuseport(sockets(4)))" in result.stdout, \
        f"eBPF config not found in output. Got:\n{result.stdout}"

@pytest.mark.features("ebpf")
def test_ebpf_config_custom_socket_no_generation():
    result = run_plugin({
        "SC4S_ENABLE_EBPF": "yes",
        "SC4S_EBPF_NO_SOCKETS": "16"
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "ebpf(reuseport(sockets(16)))" in result.stdout, \
        f"eBPF config not found in output. Got:\n{result.stdout}"

@pytest.mark.features("ebpf")
def test_disabled_ebpf_config_generation():
    result = run_plugin({
        "SC4S_ENABLE_EBPF": "no",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "ebpf(" not in result.stdout, \
        f"eBPF config should not be present. Got:\n{result.stdout}"

# =============================================================================
# TCP Parallelize Tests
# =============================================================================

@pytest.mark.features("parallelize")
def test_parallelize_enabled():
    result = run_plugin({
        "SC4S_ENABLE_PARALLELIZE": "yes",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "parallelize(partitions(4))" in result.stdout, \
        f"Parallelize config not found in output. Got:\n{result.stdout}"


@pytest.mark.features("parallelize")
def test_parallelize_custom_partitions():
    result = run_plugin({
        "SC4S_ENABLE_PARALLELIZE": "yes",
        "SC4S_PARALLELIZE_NO_PARTITION": "8",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "parallelize(partitions(8))" in result.stdout, \
        f"Parallelize config with 8 partitions not found. Got:\n{result.stdout}"


@pytest.mark.features("parallelize")
def test_parallelize_disabled():
    result = run_plugin({
        "SC4S_ENABLE_PARALLELIZE": "no",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "parallelize(" not in result.stdout, \
        f"Parallelize config should not be present. Got:\n{result.stdout}"


# =============================================================================
# UDP sockets Tests
# =============================================================================

@pytest.mark.features("udp_sockets")
def test_udp_sockets_default():
    result = run_plugin({})

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    # Default is 4 sockets, so we should see 4 persist-name entries for UDP
    assert result.stdout.count('persist-name("DEFAULT_514_') == 4, \
        f"Expected 4 UDP socket entries. Got:\n{result.stdout}"

@pytest.mark.features("udp_sockets")
def test_udp_sockets_custom():
    result = run_plugin({
        "SC4S_SOURCE_LISTEN_UDP_SOCKETS": "2",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert result.stdout.count('persist-name("DEFAULT_514_') == 2, \
        f"Expected 2 UDP socket entries. Got:\n{result.stdout}"


# =============================================================================
# Receive Buffer Tests
# =============================================================================

@pytest.mark.features("rcv_buff")
def test_udp_so_rcvbuf_enabled():
    result = run_plugin({
        "SC4S_SOURCE_UDP_SO_RCVBUFF": "16777216",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "so-rcvbuf(16777216)" in result.stdout, \
        f"so-rcvbuf config not found. Got:\n{result.stdout}"

@pytest.mark.features("rcv_buff")
def test_udp_so_rcvbuf_default():
    """
    Test that so-rcvbuf is not present when SC4S_SOURCE_UDP_SO_RCVBUFF is unset (default).
    The default behavior should match SC4S_SOURCE_UDP_SO_RCVBUFF = -1.
    """
    result = run_plugin({})
    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    # so-rcvbuf should not appear by default
    assert "so-rcvbuf(" not in result.stdout, \
        f"so-rcvbuf should not be present by default. Got:\n{result.stdout}"


# =============================================================================
# IW USE Tests
# =============================================================================

@pytest.mark.features("udp_iw")
def test_udp_iw_use_enabled():
    result = run_plugin({
        "SC4S_SOURCE_UDP_IW_USE": "yes",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "log-iw-size(250000)" in result.stdout, \
        f"log-iw-size not found in UDP config. Got:\n{result.stdout}"
    assert "log-fetch-limit(1000)" in result.stdout, \
        f"log-fetch-limit not found in UDP config. Got:\n{result.stdout}"


@pytest.mark.features("udp_iw")
def test_udp_iw_use_custom_values():
    result = run_plugin({
        "SC4S_SOURCE_UDP_IW_USE": "yes",
        "SC4S_SOURCE_UDP_IW_SIZE": "500000",
        "SC4S_SOURCE_UDP_FETCH_LIMIT": "2000",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "log-iw-size(500000)" in result.stdout, \
        f"Custom log-iw-size not found. Got:\n{result.stdout}"
    assert "log-fetch-limit(2000)" in result.stdout, \
        f"Custom log-fetch-limit not found. Got:\n{result.stdout}"


@pytest.mark.features("udp_iw")
def test_udp_iw_use_disabled():
    result = run_plugin({
        "SC4S_SOURCE_UDP_IW_USE": "no",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    # When disabled, log-iw-size should not appear in UDP network blocks
    # Note: TCP always has log-iw-size, so we check it's not in the UDP section
    output_lines = result.stdout.split('\n')
    in_udp_section = False
    udp_has_log_iw = False
    for line in output_lines:
        if 'transport("udp")' in line:
            in_udp_section = True
        elif 'transport("tcp")' in line:
            in_udp_section = False
        if in_udp_section and 'log-iw-size(' in line:
            udp_has_log_iw = True
            break
    assert not udp_has_log_iw, \
        f"log-iw-size should not be in UDP section when disabled. Got:\n{result.stdout}"


@pytest.mark.features("tcp_iw")
def test_tcp_iw_default_values():
    """
    TCP log-iw-size and log-fetch-limit are always enabled by default.
    Default values: log-iw-size=20000000, log-fetch-limit=2000
    """
    result = run_plugin({})

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "log-iw-size(20000000)" in result.stdout, \
        f"Default log-iw-size not found in TCP config. Got:\n{result.stdout}"
    assert "log-fetch-limit(2000)" in result.stdout, \
        f"Default log-fetch-limit not found in TCP config. Got:\n{result.stdout}"


@pytest.mark.features("tcp_iw")
def test_tcp_iw_custom_values():
    """
    TCP log-iw-size and log-fetch-limit can be customized via environment variables.
    """
    result = run_plugin({
        "SC4S_SOURCE_TCP_IW_SIZE": "50000000",
        "SC4S_SOURCE_TCP_FETCH_LIMIT": "5000",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "log-iw-size(50000000)" in result.stdout, \
        f"Custom log-iw-size not found in TCP config. Got:\n{result.stdout}"
    assert "log-fetch-limit(5000)" in result.stdout, \
        f"Custom log-fetch-limit not found in TCP config. Got:\n{result.stdout}"


# =============================================================================
# IPv6 Enable Tests
# =============================================================================

@pytest.mark.features("ipv6")
def test_ipv6_enabled():
    result = run_plugin({
        "SC4S_IPV6_ENABLE": "yes",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "ip-protocol(6)" in result.stdout, \
        f"IPv6 protocol not found. Got:\n{result.stdout}"
    assert "ip-protocol(4)" not in result.stdout, \
        f"IPv4 protocol should not be present when IPv6 enabled. Got:\n{result.stdout}"


@pytest.mark.features("ipv6")
def test_ipv6_disabled():
    result = run_plugin({
        "SC4S_IPV6_ENABLE": "no",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "ip-protocol(4)" in result.stdout, \
        f"IPv4 protocol not found. Got:\n{result.stdout}"
    assert "ip-protocol(6)" not in result.stdout, \
        f"IPv6 protocol should not be present when disabled. Got:\n{result.stdout}"


# =============================================================================
# Disk Buffer Tests (HEC Destination)
# =============================================================================

@pytest.mark.features("disk_buffer")
def test_disk_buffer_enabled_by_default():
    """
    Disk buffer is enabled by default for HEC destination.
    """
    result = run_dest_hec_plugin({})

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "disk-buffer(" in result.stdout, \
        f"Disk buffer should be enabled by default. Got:\n{result.stdout}"
    assert "reliable(no)" in result.stdout, \
        f"Default should be non-reliable mode. Got:\n{result.stdout}"


@pytest.mark.features("disk_buffer")
def test_disk_buffer_disabled():
    """
    Disk buffer can be disabled via environment variable.
    """
    result = run_dest_hec_plugin({
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE": "no",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "disk-buffer(" not in result.stdout, \
        f"Disk buffer should not be present when disabled. Got:\n{result.stdout}"


@pytest.mark.features("disk_buffer")
def test_disk_buffer_reliable_mode():
    """
    Disk buffer can be configured for reliable mode.
    """
    result = run_dest_hec_plugin({
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE": "yes",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "disk-buffer(" in result.stdout, \
        f"Disk buffer not found. Got:\n{result.stdout}"
    assert "reliable(yes)" in result.stdout, \
        f"Reliable mode should be enabled. Got:\n{result.stdout}"
    assert "mem-buf-size(" in result.stdout, \
        f"mem-buf-size should be present in reliable mode. Got:\n{result.stdout}"


@pytest.mark.features("disk_buffer")
def test_disk_buffer_custom_sizes():
    """
    Disk buffer sizes can be customized via environment variables.
    """
    result = run_dest_hec_plugin({
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE": "yes",
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE": "50000000",
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE": "1000000000",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert "mem-buf-size(50000000)" in result.stdout, \
        f"Custom mem-buf-size not found. Got:\n{result.stdout}"
    assert "disk-buf-size(1000000000)" in result.stdout, \
        f"Custom disk-buf-size not found. Got:\n{result.stdout}"


@pytest.mark.features("disk_buffer")
def test_disk_buffer_custom_directory():
    """
    Disk buffer directory can be customized (for BYOE setups).
    """
    result = run_dest_hec_plugin({
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DIR": "/var/syslog-ng/buffer",
    })

    assert result.returncode == 0, f"Failed to generate config: {result.stderr}"
    assert 'dir("/var/syslog-ng/buffer")' in result.stdout, \
        f"Custom buffer directory not found. Got:\n{result.stdout}"
