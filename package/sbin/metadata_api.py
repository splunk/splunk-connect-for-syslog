import csv
import io
import logging
import re
import shutil
from pathlib import Path

from flask import Blueprint, jsonify, request

from config_api import csrf, restart_syslog_ng, syntax_check

logger = logging.getLogger(__name__)

metadata_bp = Blueprint("metadata", __name__)

CONTEXT_DIR = Path("/etc/syslog-ng/conf.d/local/context")

SPLUNK_METADATA_CSV = CONTEXT_DIR / "splunk_metadata.csv"
COMPLIANCE_CONF = CONTEXT_DIR / "compliance_meta_by_source.conf"
COMPLIANCE_CSV = CONTEXT_DIR / "compliance_meta_by_source.csv"
VPS_CONF = CONTEXT_DIR / "vendor_product_by_source.conf"
VPS_CSV = CONTEXT_DIR / "vendor_product_by_source.csv"
HOST_CSV = CONTEXT_DIR / "host.csv"

SPLUNK_METADATA_FIELDS = {"index", "source", "sourcetype", "host", "sc4s_template"}

COMPLIANCE_FIELD_RE = re.compile(
    r"^(\.splunk\.(index|source|sourcetype)|fields\.[a-zA-Z0-9_]+)$"
)

FILTER_BLOCK_RE = re.compile(
    r"filter\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\{[^}]*\}\s*;", re.DOTALL
)


def _read_three_col_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            rows.append({"col1": row[0].strip(), "col2": row[1].strip(), "col3": row[2].strip()})
    return rows


def _backup(path: Path) -> Path:
    backup = path.with_suffix(path.suffix + ".backup")
    if path.exists():
        shutil.copy(path, backup)
    return backup


def _rollback(backups: list[tuple[Path, Path]]):
    for original, backup in backups:
        if backup.exists():
            shutil.copy(backup, original)
            backup.unlink()
        elif original.exists():
            original.unlink()


def _cleanup_backups(backups: list[tuple[Path, Path]]):
    for _, backup in backups:
        if backup.exists():
            backup.unlink()


def _apply_with_rollback(files_to_write: dict[Path, str]):
    """Write files, run syntax check + restart, rollback on failure."""
    backups = []
    try:
        for path, content in files_to_write.items():
            backups.append((path, _backup(path)))
            path.write_text(content, encoding="utf-8")

        syntax_check()
        restart_syslog_ng()
    except Exception as e:
        logger.exception("Metadata update failed, rolling back")
        _rollback(backups)
        raise e
    finally:
        _cleanup_backups(backups)

# ---------------------------------------------------------------------------
# splunk_metadata.csv
# ---------------------------------------------------------------------------

@metadata_bp.route("/config/metadata/splunk", methods=["GET"])
def get_splunk_metadata():
    rows = _read_three_col_csv(SPLUNK_METADATA_CSV)
    entries = [{"key": r["col1"], "metadata": r["col2"], "value": r["col3"]} for r in rows]
    return jsonify({"entries": entries}), 200


@csrf.exempt
@metadata_bp.route("/config/metadata/splunk", methods=["POST"])
def set_splunk_metadata():
    data = request.get_json(silent=True)
    if not data or "entries" not in data:
        return jsonify({"status": "error", "message": "JSON body with 'entries' required"}), 400

    entries = data["entries"]
    for entry in entries:
        if not all(k in entry for k in ("key", "metadata", "value")):
            return jsonify({"status": "error", "message": "Each entry must have 'key', 'metadata', 'value'"}), 400
        if entry["metadata"] not in SPLUNK_METADATA_FIELDS:
            return jsonify({
                "status": "error",
                "message": f"Invalid metadata field '{entry['metadata']}'. Allowed: {sorted(SPLUNK_METADATA_FIELDS)}",
            }), 400

    buf = io.StringIO()
    writer = csv.writer(buf)
    for entry in entries:
        writer.writerow([entry["key"], entry["metadata"], entry["value"]])

    try:
        _apply_with_rollback({SPLUNK_METADATA_CSV: buf.getvalue()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "metadata updated successfully", "entries": entries}), 200


@csrf.exempt
@metadata_bp.route("/config/metadata/splunk", methods=["DELETE"])
def delete_splunk_metadata():
    if not SPLUNK_METADATA_CSV.exists():
        return jsonify({"status": "error", "message": "splunk_metadata.csv not found"}), 404

    try:
        _apply_with_rollback({SPLUNK_METADATA_CSV: ""})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "splunk_metadata.csv cleared successfully"}), 200


# ---------------------------------------------------------------------------
# compliance_meta_by_source (.conf + .csv)
# ---------------------------------------------------------------------------

@metadata_bp.route("/config/metadata/compliance", methods=["GET"])
def get_compliance():
    conf_text = COMPLIANCE_CONF.read_text(encoding="utf-8") if COMPLIANCE_CONF.exists() else ""
    rows = _read_three_col_csv(COMPLIANCE_CSV)
    csv_content = [{"filter_name": r["col1"], "field_name": r["col2"], "value": r["col3"]} for r in rows]
    return jsonify({"conf_content": conf_text, "csv_content": csv_content}), 200


@csrf.exempt
@metadata_bp.route("/config/metadata/compliance", methods=["POST"])
def set_compliance():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "JSON body required"}), 400

    conf_content = data.get("conf_content", "")
    csv_content = data.get("csv_content", [])

    if not conf_content and not csv_content:
        return jsonify({"status": "error", "message": "No conf_content or csv_content provided"}), 400

    for entry in csv_content:
        if not all(k in entry for k in ("filter_name", "field_name", "value")):
            return jsonify({"status": "error", "message": "Each entry must have 'filter_name', 'field_name', 'value'"}), 400
        if not COMPLIANCE_FIELD_RE.match(entry["field_name"]):
            return jsonify({
                "status": "error",
                "message": (
                    f"Invalid field_name '{entry['field_name']}'. "
                    "Must be .splunk.index, .splunk.source, .splunk.sourcetype, or fields.<name>"
                ),
            }), 400

    if conf_content and csv_content:
        defined_filters = set(FILTER_BLOCK_RE.findall(conf_content))
        csv_filters = {e["filter_name"] for e in csv_content}
        orphaned = csv_filters - defined_filters
        if orphaned:
            return jsonify({
                "status": "error",
                "message": f"csv_content references filters not defined in conf_content: {sorted(orphaned)}",
            }), 400

    files_to_write = {}
    if conf_content:
        files_to_write[COMPLIANCE_CONF] = conf_content.strip() + "\n"
    if csv_content:
        buf = io.StringIO()
        writer = csv.writer(buf)
        for entry in csv_content:
            writer.writerow([entry["filter_name"], entry["field_name"], entry["value"]])
        files_to_write[COMPLIANCE_CSV] = buf.getvalue()

    try:
        _apply_with_rollback(files_to_write)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "compliance metadata updated successfully"}), 200


@csrf.exempt
@metadata_bp.route("/config/metadata/compliance", methods=["DELETE"])
def delete_compliance():
    if not COMPLIANCE_CONF.exists() and not COMPLIANCE_CSV.exists():
        return jsonify({"status": "error", "message": "compliance_meta_by_source files not found"}), 404

    files_to_write = {}
    if COMPLIANCE_CONF.exists():
        files_to_write[COMPLIANCE_CONF] = ""
    if COMPLIANCE_CSV.exists():
        files_to_write[COMPLIANCE_CSV] = ""

    try:
        _apply_with_rollback(files_to_write)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "compliance metadata cleared successfully"}), 200