from app import mcp, REPO_ROOT
from utils.file_utils import read_dir_markdown

CREATING_PARSERS_DIR = REPO_ROOT / "docs" / "creating_parsers"

CREATING_PARSERS_FILES = [
    "index.md",
    "filter_message.md",
    "parse_message.md",
    "unit_tests.md",
]


@mcp.resource("sc4s://docs/creating_parsers")
def creating_parsers_guide() -> str:
    """Full parser creation guide including filters and unit tests."""
    sections = []
    for filename in CREATING_PARSERS_FILES:
        filepath = CREATING_PARSERS_DIR / filename
        if filepath.exists():
            sections.append(filepath.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(sections)


@mcp.resource("sc4s://docs/troubleshooting")
def troubleshooting_guide() -> str:
    """SC4S troubleshooting reference covering health checks, PCAP testing, and common issues."""
    return read_dir_markdown(REPO_ROOT / "docs" / "troubleshooting")


@mcp.resource("sc4s://docs/vendor/{vendor}")
def vendor_docs(vendor: str) -> str:
    """Documentation for a specific vendor's log sources supported by SC4S."""
    vendor_dir = REPO_ROOT / "docs" / "sources" / "vendor" / vendor
    return read_dir_markdown(vendor_dir)
