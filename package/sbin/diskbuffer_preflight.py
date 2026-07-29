#!/usr/bin/env python3
"""Preflight check: confirm the syslog-ng disk buffer can be locked.

syslog-ng guards each disk-buffer directory with a "dirlock" file that it locks
via flock(2). Ephemeral, overlay, and some network filesystems (notably AWS
Fargate's ephemeral task storage) do not support this lock, so syslog-ng aborts
at runtime with a cryptic message and then crash-loops:

    Failed to grab disk-buffer dirlock;
    filename='/var/lib/syslog-ng/syslog-ng-disk-buffer.dirlock',
    error='Bad file descriptor (9)'

This script reproduces the same flock() on the same directory *before* syslog-ng
starts, so the entrypoint can fail fast with an actionable message instead of
letting the cryptic error scroll past in a restart loop. It is invoked from
entrypoint.sh after configuration has been validated. Set
SC4S_DISKBUFF_PREFLIGHT=no to skip it.

Exit codes:
    0 - disk buffer disabled, or every buffer directory supports locking
    1 - disk buffer enabled but a buffer directory cannot be locked (abort startup)
"""
import fcntl
import os
import re
import subprocess
import sys

DOC_URL = "https://splunk.github.io/splunk-connect-for-syslog/main/gettingstarted/ecs-fargate/"
PROBE_NAME = ".sc4s-diskbuffer-preflight.lock"


def _disk_buffer_blocks(config: str) -> list[str]:
    """Return the text of each `disk-buffer( ... )` block in the config.

    Scans with a parenthesis counter so nested options (mem-buf-size(...),
    disk-buf-size(...), etc.) don't truncate the block early.
    """
    blocks = []
    token = "disk-buffer("
    idx = 0
    while True:
        start = config.find(token, idx)
        if start == -1:
            break
        # Walk from the '(' of disk-buffer( to its matching ')'.
        depth = 0
        j = start + len(token) - 1
        while j < len(config):
            char = config[j]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blocks.append(config[start:j + 1])
        idx = j + 1
    return blocks


def diskbuffer_dirs() -> set[str]:
    """Return the directories syslog-ng will place a disk buffer in.

    Asks syslog-ng for its fully-resolved config (`--preprocess-into=-`) so we
    reflect the actual outcome of every SC4S_..._DISKBUFF_ENABLE default and
    override rather than re-deriving that logic here. If a disk-buffer() block
    declares an explicit dir("..."), the buffer (and its dirlock) lives there;
    otherwise syslog-ng uses SC4S_VAR, which is the default and the location in
    the reported failure.
    """
    sc4s_var = os.getenv("SC4S_VAR", "/var/lib/syslog-ng")
    try:
        config = subprocess.run(
            ["syslog-ng", "--no-caps", "--preprocess-into=-"],
            capture_output=True,
            text=True,
            timeout=60,
        ).stdout
    except Exception as exc:  # noqa: BLE001 - the probe must never abort startup itself
        print(f"SC4S_ENV_CHECK_DISKBUFF: could not read syslog-ng config ({exc}); skipping preflight.")
        return set()

    blocks = _disk_buffer_blocks(config)
    if not blocks:
        return set()  # disk buffer disabled everywhere -> nothing to check

    explicit = set()
    for block in blocks:
        explicit.update(re.findall(r'dir\(\s*"([^"]+)"\s*\)', block))
    return explicit or {sc4s_var}


def can_lock(directory: str):
    """Try to create and flock() a throwaway probe file in `directory`.

    Uses the same flock(LOCK_EX) syslog-ng's dirlock uses, on the same path, so
    a filesystem that fails here is exactly one that would fail syslog-ng.
    Returns (True, None) on success or (False, OSError) on failure.
    """
    probe = os.path.join(directory, PROBE_NAME)
    fd = None
    try:
        fd = os.open(probe, os.O_CREAT | os.O_RDWR, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return True, None
    except OSError as exc:
        return False, exc
    finally:
        if fd is not None:
            os.close(fd)
            try:
                os.unlink(probe)
            except OSError:
                pass


def main() -> int:
    dirs = diskbuffer_dirs()
    if not dirs:
        return 0

    failures = []
    for directory in sorted(dirs):
        if not os.path.isdir(directory):
            # syslog-ng would create it later; we can't probe what isn't there yet.
            continue
        ok, exc = can_lock(directory)
        if ok:
            print(f"SC4S_ENV_CHECK_DISKBUFF: '{directory}' supports the disk-buffer lock. OK")
        else:
            failures.append((directory, exc))

    if not failures:
        return 0

    for directory, exc in failures:
        print(
            "SC4S_ENV_CHECK_DISKBUFF: FATAL - the disk buffer is enabled but its "
            f"directory '{directory}' does not support the file locking that "
            f"syslog-ng requires ({exc}).\n"
            "This is typical of ephemeral or overlay storage such as AWS Fargate "
            "task storage.\n"
            "\n"
            "Fix ONE of the following:\n"
            "  1. Mount storage that supports file locking (for example AWS EFS, or\n"
            f"     an EBS/host volume) at {os.getenv('SC4S_VAR', '/var/lib/syslog-ng')}, OR\n"
            "  2. Disable the disk buffer by setting:\n"
            "       SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE=no\n"
            "     WARNING: without the disk buffer, events are held in memory only and\n"
            "     are LOST if Splunk is unreachable or the container stops.\n"
            "\n"
            f"See: {DOC_URL}\n"
            "Refusing to start to avoid a crash-loop. "
            "(Set SC4S_DISKBUFF_PREFLIGHT=no to bypass this check.)"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
