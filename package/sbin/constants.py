from pathlib import Path
import re


ENV_FILE = Path("/opt/sc4s/env_file")
BACKUP_FILE = ENV_FILE.with_suffix(".backup")
PARSERS_DIR = Path("/etc/syslog-ng/conf.d/local/config/app_parsers")

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
