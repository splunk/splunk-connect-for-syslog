import pytest
import json
import subprocess


def bpftool_available():
    """Check if bpftool is available on the host system."""
    try:
        result = subprocess.run(
            ["bpftool", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

@pytest.mark.features("ebpf")
def test_socket_filter_programs_loaded():
    """
    Verify that socket_filter eBPF programs are loaded when SC4S 
    is configured with eBPF enabled.
    
    Note: This test requires SC4S to be running with SC4S_ENABLE_EBPF=yes
    """
    if not bpftool_available():
        pytest.skip("bpftool not available")
    
    result = subprocess.run(
        ["sudo", "bpftool", "prog", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0, f"bpftool failed: {result.stderr}"
    
    programs = json.loads(result.stdout) if result.stdout.strip() else []
    print(programs)

    # Look for socket_filter type programs (used by syslog-ng eBPF)
    socket_filter_progs = [
        p for p in programs
        if p.get('type') == 'socket_filter' and p.get('name') == 'random_choice'
    ]
    
    print(f"Found {len(socket_filter_progs)} socket_filter eBPF programs")
    
    for prog in socket_filter_progs:
        print(f"  ID: {prog.get('id')}, Name: {prog.get('name', 'N/A')}")
    
    assert len(socket_filter_progs) > 0, "No socket_filter eBPF programs found."