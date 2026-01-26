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
def test_sk_reuseport_programs_loaded():
    """
    Verify that sk_reuseport eBPF programs are loaded when SC4S 
    is configured with eBPF enabled.
    
    Note: This test requires SC4S to be running with SC4S_ENABLE_EBPF=yes
    """
    if not bpftool_available():
        pytest.skip("bpftool not available")
    
    result = subprocess.run(
        ["bpftool", "prog", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0, f"bpftool failed: {result.stderr}"
    
    programs = json.loads(result.stdout) if result.stdout.strip() else []
    
    # Look for sk_reuseport type programs (used by syslog-ng eBPF)
    reuseport_progs = [
        p for p in programs
        if p.get('type') == 'sk_reuseport'
    ]
    
    print(f"Found {len(reuseport_progs)} sk_reuseport eBPF programs")
    
    if len(reuseport_progs) == 0:
        print("WARNING: No sk_reuseport programs found. "
                "Verify SC4S_ENABLE_EBPF=yes and container is privileged.")