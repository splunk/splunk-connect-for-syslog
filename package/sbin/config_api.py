import logging

from flask_wtf.csrf import CSRFProtect
from flask import Blueprint, jsonify, request

from package.sbin.constants import ENV_FILE, PARSERS_DIR
from package.sbin.utils import apply_with_rollback

logger = logging.getLogger(__name__)

config_bp = Blueprint("config", __name__)
csrf = CSRFProtect()


@config_bp.route("/config/env", methods=["GET"])
def get_env():
    if not ENV_FILE.exists():
        return jsonify({"status": "error", "message": "env_file not found"}), 404

    return jsonify(
        {
            "path": str(ENV_FILE),
            "content": ENV_FILE.read_text(encoding="utf-8"),
        }
    ), 200


@csrf.exempt
@config_bp.route("/config/env", methods=["POST"])
def set_env():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "no file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "empty file"}), 400

    try:
        apply_with_rollback({ENV_FILE: file.read().decode("utf-8")})
    except Exception as e:
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

    try:
        apply_with_rollback({parser_path: file.read().decode("utf-8")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify(
        {"status": "parser added successfully", "path": str(parser_path)}
    ), 200


@config_bp.route("/config/parser/<name>", methods=["GET"])
def get_parser(name):
    if not name.endswith(".conf"):
        name += ".conf"

    parser_path = PARSERS_DIR / name
    if not parser_path.exists():
        return jsonify({"status": "error", "message": "parser not found"}), 404

    return jsonify(
        {
            "name": name,
            "content": parser_path.read_text(encoding="utf-8"),
        }
    ), 200


@csrf.exempt
@config_bp.route("/config/parser/<name>", methods=["DELETE"])
def delete_parser(name):
    if not name.endswith(".conf"):
        name += ".conf"

    parser_path = PARSERS_DIR / name
    if not parser_path.exists():
        return jsonify({"status": "error", "message": "parser not found"}), 404

    try:
        apply_with_rollback({parser_path: None})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "parser deleted successfully"}), 200


@config_bp.route("/config/parsers", methods=["GET"])
def list_parsers():
    parsers = [f.name for f in PARSERS_DIR.glob("*.conf")]
    return jsonify({"parsers": parsers}), 200
