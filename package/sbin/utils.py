import csv
import os
import logging
from pathlib import Path
import subprocess
import shutil
import time
from typing import Callable

from constants import ENV_FILE

logger = logging.getLogger(__name__)

RESTART_TIMEOUT_SECONDS = 30
RELOAD_TIMEOUT_SECONDS = 30
RESTART_POLL_INTERVAL_SECONDS = 0.5
RELOAD_POLL_INTERVAL_SECONDS = 0.5


def build_env_from_file():
    """Build environment dict from current env_file."""
    env = os.environ.copy()
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def _get_syslog_ng_pids() -> set[int]:
    result = subprocess.run(
        ["pgrep", "-x", "syslog-ng"],
        capture_output=True,
        text=True,
        timeout=1,
    )
    if result.returncode == 1:
        return set()
    if result.returncode != 0:
        raise RuntimeError(
            f"failed to find syslog-ng processes: {result.stderr.strip()}"
        )

    return {int(pid) for pid in result.stdout.split()}


def _syslog_ng_is_healthy() -> bool:
    try:
        result = subprocess.run(
            ["syslog-ng-ctl", "healthcheck", "--timeout", "1"],
            capture_output=True,
            text=True,
            timeout=2,
        )
    except subprocess.TimeoutExpired:
        return False

    return result.returncode == 0


def restart_syslog_ng():
    """Restart syslog-ng and wait for its replacement to become healthy."""
    previous_pids = _get_syslog_ng_pids()
    result = subprocess.run(
        ["pkill", "syslog-ng"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"syslog-ng restart failed: {result.stderr.strip()}")

    deadline = time.monotonic() + RESTART_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        current_pids = _get_syslog_ng_pids()
        replacement_is_healthy = (
            bool(current_pids - previous_pids) and _syslog_ng_is_healthy()
        )
        remaining = deadline - time.monotonic()
        if replacement_is_healthy and remaining > 0:
            return
        if remaining <= 0:
            break
        time.sleep(min(RESTART_POLL_INTERVAL_SECONDS, remaining))

    raise RuntimeError(
        f"syslog-ng restart timed out after {RESTART_TIMEOUT_SECONDS} seconds"
    )


def reload_syslog_ng():
    """Reload syslog-ng using syslog-ng-ctl reload command, aka send SIGHUP."""
    previous_pids = _get_syslog_ng_pids()
    result = subprocess.run(
        ["syslog-ng-ctl", "reload"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"syslog-ng reload failed: {error}")
    deadline = time.monotonic() + RELOAD_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        current_pids = _get_syslog_ng_pids()
        replacement_is_healthy = (
            bool(current_pids == previous_pids) and _syslog_ng_is_healthy()
        )
        remaining = deadline - time.monotonic()
        if replacement_is_healthy and remaining > 0:
            return
        if remaining <= 0:
            break
        time.sleep(min(RELOAD_POLL_INTERVAL_SECONDS, remaining))

    raise RuntimeError(
        f"syslog-ng reload timed out after {RELOAD_TIMEOUT_SECONDS} seconds"
    )


def syntax_check():
    """Validate the syslog-ng configuration using env from the current env_file."""
    result = subprocess.run(
        ["syslog-ng", "--no-caps", "-s"],
        capture_output=True,
        text=True,
        timeout=30,
        env=build_env_from_file(),
    )
    if result.returncode != 0:
        raise RuntimeError(f"syslog-ng syntax check failed: {result.stderr.strip()}")


def read_three_col_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            rows.append(
                {"col1": row[0].strip(), "col2": row[1].strip(), "col3": row[2].strip()}
            )
    return rows


def backup_file(path: Path) -> Path:
    backup = path.with_suffix(path.suffix + ".backup")
    if path.exists():
        shutil.copy(path, backup)
    return backup


def rollback(backups: list[tuple[Path, Path]]):
    for original, backup in backups:
        if backup.exists():
            shutil.copy(backup, original)
            backup.unlink()
        elif original.exists():
            original.unlink()


def cleanup_backups_files(backups: list[tuple[Path, Path]]):
    for _, backup in backups:
        if backup.exists():
            backup.unlink()


def apply_with_rollback(
    files_to_write: dict[Path, str | None], restart_func: Callable[[], None]
):
    """Write files, validate and restart.

    Restore both files and runtime on failure.
    """
    backups = []
    runtime_restart_started = False
    try:
        for path, content in files_to_write.items():
            backups.append((path, backup_file(path)))
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(content, encoding="utf-8")

        syntax_check()
        runtime_restart_started = True
        restart_func()
    except Exception as apply_error:
        logger.exception("Apply failed, rolling back")
        try:
            rollback(backups)
            if runtime_restart_started:
                restart_func()
        except Exception as rollback_error:
            logger.exception("Rollback failed")
            raise RuntimeError(
                f"configuration apply failed: {apply_error}; "
                f"rollback failed: {rollback_error}"
            ) from rollback_error
        raise
    finally:
        cleanup_backups_files(backups)
