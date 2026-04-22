import logging
import os
from pathlib import Path
import shutil
import subprocess

from flask_wtf.csrf import CSRFProtect
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

config_bp = Blueprint("config", __name__)
csrf = CSRFProtect()

ENV_FILE = Path("/opt/sc4s/env_file")
BACKUP_FILE = ENV_FILE.with_suffix(".backup")
PARSERS_DIR = Path("/etc/syslog-ng/conf.d/local/config/app_parsers")


def _build_env_from_file():
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
        env=_build_env_from_file(),
    )
    if result.returncode != 0:
        raise RuntimeError(f"syslog-ng syntax check failed: {result.stderr.strip()}")


@config_bp.route("/config/env", methods=["GET"])
def get_env():
    if not ENV_FILE.exists():
        return jsonify({"status": "error", "message": "env_file not found"}), 404

    return jsonify({
        "path": str(ENV_FILE),
        "content": ENV_FILE.read_text(encoding="utf-8"),
    }), 200


@csrf.exempt
@config_bp.route("/config/env", methods=["POST"])
def set_env():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "no file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "empty file"}), 400

    shutil.copy(ENV_FILE, BACKUP_FILE)

    try:
        with open(ENV_FILE, "w") as env_f:
            env_f.write(file.read().decode("utf-8"))

        restart_syslog_ng()
    except Exception as e:
        logger.exception("Failed to apply env_file update, rolling back")
        rollback_env()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "env_file updated successfully"}), 200


@csrf.exempt
@config_bp.route("/config/parser", methods=["POST"])
def add_parser():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "no file provided"}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.endswith(".conf"):
        return jsonify({"status": "error", "message": "file must be a .conf file"}), 400

    parser_path = PARSERS_DIR / file.filename
    backup_path = parser_path.with_suffix(".conf.backup") if parser_path.exists() else None

    if backup_path:
        shutil.copy(parser_path, backup_path)

    try:
        file.save(parser_path)
        syntax_check()
        restart_syslog_ng()
    except Exception as e:
        logger.exception("Failed to apply parser, rolling back")
        if backup_path and backup_path.exists():
            shutil.copy(backup_path, parser_path)
        elif parser_path.exists():
            parser_path.unlink()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if backup_path and backup_path.exists():
            backup_path.unlink()

    return jsonify({"status": "parser added successfully", "path": str(parser_path)}), 200


@config_bp.route("/config/parser/<name>", methods=["GET"])
def get_parser(name):
    if not name.endswith(".conf"):
        name += ".conf"

    parser_path = PARSERS_DIR / name
    if not parser_path.exists():
        return jsonify({"status": "error", "message": "parser not found"}), 404

    return jsonify({
        "name": name,
        "content": parser_path.read_text(encoding="utf-8"),
    }), 200


@csrf.exempt
@config_bp.route("/config/parser/<name>", methods=["DELETE"])
def delete_parser(name):
    if not name.endswith(".conf"):
        name += ".conf"

    parser_path = PARSERS_DIR / name
    if not parser_path.exists():
        return jsonify({"status": "error", "message": "parser not found"}), 404

    backup_path = parser_path.with_suffix(".conf.backup")
    shutil.copy(parser_path, backup_path)

    try:
        parser_path.unlink()
        syntax_check()
        restart_syslog_ng()
    except Exception as e:
        logger.exception("Failed to delete parser, rolling back")
        shutil.copy(backup_path, parser_path)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if backup_path.exists():
            backup_path.unlink()

    return jsonify({"status": "parser deleted successfully"}), 200


@config_bp.route("/config/parsers", methods=["GET"])
def list_parsers():
    parsers = [f.name for f in PARSERS_DIR.glob("*.conf")]
    return jsonify({"parsers": parsers}), 200
