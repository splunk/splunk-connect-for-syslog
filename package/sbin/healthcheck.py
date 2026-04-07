import logging
import os
from pathlib import Path
import shutil
import subprocess
import re

from flask_wtf.csrf import CSRFProtect
from flask import Flask, jsonify, request

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

def str_to_bool(value):
    return str(value).strip().lower() in {
        'true', 
        '1',
        't',
        'y',
        'yes'
    }

def get_list_of_destinations():
    found_destinations = []
    regex = r"^SC4S_DEST_SPLUNK_HEC_(.*)_URL$"

    for var_key, var_variable in os.environ.items():
        if re.search(regex, var_key):
            found_destinations.append(var_variable)
    return set(found_destinations)

class Config:
    HEALTHCHECK_PORT = int(os.getenv('SC4S_LISTEN_STATUS_PORT', '8080'))
    CHECK_QUEUE_SIZE = str_to_bool(os.getenv('HEALTHCHECK_CHECK_QUEUE_SIZE', "false"))
    MAX_QUEUE_SIZE = int(os.getenv('HEALTHCHECK_MAX_QUEUE_SIZE', '10000'))
    DESTINATIONS = get_list_of_destinations()

logging.basicConfig(
    format="%(asctime)s - healthcheck.py - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def check_syslog_ng_health() -> bool:
    """Check the health of the syslog-ng process."""
    try:
        result = subprocess.run(
            ['syslog-ng-ctl', 'healthcheck', '-t', '1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
        
        logger.error(f"syslog-ng healthcheck failed: {result.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("syslog-ng healthcheck timed out.")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during syslog-ng healthcheck: {e}")
        return False

def check_queue_size(
        sc4s_dest_splunk_hec_destinations=Config.DESTINATIONS,
        max_queue_size=Config.MAX_QUEUE_SIZE
    ) -> bool:
    """Check syslog-ng queue size and compare it against the configured maximum limit."""
    if not sc4s_dest_splunk_hec_destinations:
        logger.error(
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_URL not configured. "
            "Ensure the default HEC destination is set, or disable HEALTHCHECK_CHECK_QUEUE_SIZE."
        )
        return False

    try:
        result = subprocess.run(
            ['syslog-ng-ctl', 'stats'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.error(f"syslog-ng stats command failed: {result.stderr.strip()}")
            return False

        stats = result.stdout.splitlines()

        queue_sizes_all_destinations = []

        for destination in sc4s_dest_splunk_hec_destinations:
            destination_stat = next(
                (s for s in stats if ";queued;" in s and destination in s),
                None
            )

            if not destination_stat:
                logger.error(f"No matching queue stats found for the destination URL {destination}.")
                return False

            queue_sizes_all_destinations.append(int(destination_stat.split(";")[-1]))

        queue_size = max(queue_sizes_all_destinations)
        if queue_size > max_queue_size:
            logger.warning(
                f"Queue size {queue_size} exceeds the maximum limit of {max_queue_size}."
            )
            return False

        return True
    except subprocess.TimeoutExpired:
        logger.error("syslog-ng stats command timed out.")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error checking queue size: {e}")
        return False

@app.route('/health', methods=['GET'])
def healthcheck():
    if Config.CHECK_QUEUE_SIZE:
        if not check_syslog_ng_health():
            return jsonify({'status': 'unhealthy: syslog-ng healthcheck failed'}), 503
        if not check_queue_size():
            return jsonify({'status': 'unhealthy: queue size exceeded limit'}), 503
    else:
        if not check_syslog_ng_health():
            return jsonify({'status': 'unhealthy: syslog-ng healthcheck failed'}), 503

    logger.info("Service is healthy.")
    return jsonify({'status': 'healthy'}), 200


ENV_FILE = Path("/opt/sc4s/env_file")
BACKUP_FILE = ENV_FILE.with_suffix(".backup")


def load_env_file(path):
    """Parse KEY=VALUE lines from env_file and apply them to os.environ."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ[key.strip()] = value.strip()


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
        load_env_file(ENV_FILE)
        try:
            restart_syslog_ng()
        except Exception:
            logger.exception("Rollback also failed")


@csrf.exempt
@app.route("/config/env", methods=["POST"])
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

        load_env_file(ENV_FILE)
        restart_syslog_ng()
    except Exception as e:
        logger.exception("Failed to apply env_file update, rolling back")
        rollback_env()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "env_file updated successfully"}), 200

PARSERS_DIR = Path("/etc/syslog-ng/conf.d/local/config/app_parsers")


def syntax_check():
    """Validate the syslog-ng configuration."""
    result = subprocess.run(
        ["syslog-ng", "--no-caps", "-s"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"syslog-ng syntax check failed: {result.stderr.strip()}")


@csrf.exempt
@app.route("/config/parser", methods=["POST"])
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


@csrf.exempt
@app.route("/config/parser/<name>", methods=["DELETE"])
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


@csrf.exempt
@app.route("/config/parsers", methods=["GET"])
def list_parsers():
    parsers = [f.name for f in PARSERS_DIR.glob("*.conf")]
    return jsonify({"parsers": parsers}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.HEALTHCHECK_PORT)