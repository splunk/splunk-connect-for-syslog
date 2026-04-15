import csv
import os
import logging
from pathlib import Path
import subprocess
import shutil

from package.sbin.constants import BACKUP_FILE, ENV_FILE

logger = logging.getLogger(__name__)


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


def restart_syslog_ng():
    """Kill syslog-ng; the entrypoint while loop will restart it automatically."""
    result = subprocess.run(
        ["pkill", "syslog-ng"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"syslog-ng restart failed: {result.stderr.strip()}")


def rollback_env():
    """Restore env_file from backup and restart syslog-ng."""
    if BACKUP_FILE.exists():
        shutil.copy(BACKUP_FILE, ENV_FILE)
        try:
            restart_syslog_ng()
        except Exception:
            logger.exception("Rollback also failed")


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


def apply_with_rollback(files_to_write: dict[Path, str | None]):
    """Write files (or delete if content is None), run syntax check + restart, rollback on failure."""
    backups = []
    try:
        for path, content in files_to_write.items():
            backups.append((path, backup_file(path)))
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(content, encoding="utf-8")

        syntax_check()
        restart_syslog_ng()
    except Exception as e:
        logger.exception("Apply failed, rolling back")
        rollback(backups)
        raise e
    finally:
        cleanup_backups_files(backups)
