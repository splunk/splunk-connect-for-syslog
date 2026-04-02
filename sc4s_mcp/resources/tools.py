from pathlib import Path
import re
from app import mcp

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

@mcp.tool
def list_vendors() -> list[str]:
    """Lists all vendors supported by SC4S, based on the directories from known sources page in docs"""
    sources_vendor_dir = REPO_ROOT / "docs" / "sources" / "vendor"
    return list(Path(sources_vendor_dir).iterdir())

@mcp.tool
def list_all_parsers() -> list[str]:
    """Lists all parses, based on the .conf files in addon directory"""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    return list(Path(addons_dir).rglob("*.conf"))

@mcp.tool
def list_vendor_parsers(vendor: str) -> list[str]:
    """Lists parses for given vendor, based on the parsers in addon directory"""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    results = []
    vendor_pattern = re.compile(rf"\b{re.escape(vendor)}\b", re.IGNORECASE)

    for conf_file in Path(addons_dir).rglob("*.conf"):
        try:
            content = conf_file.read_text(encoding='utf-8')
        except Exception:
            continue
        if vendor_pattern.search(content):
            results.append(str(conf_file))

    return results

@mcp.tool
def get_parser(parser_name: str) -> list[str]:
    """Get parser with this name from addon library"""
    addons_dir = REPO_ROOT / "package" / "lite" / "etc" / "addons"
    return list(Path(addons_dir).rglob("*.conf"))
    

@mcp.tool
def search_docs(query: str) -> list[str]:
    """
    Full text search for a pattern in the documentation files within docs/. Returns matching lines, including filename and line number.
    """
    docs_dir = REPO_ROOT / "docs"
    results = []
    pattern = re.compile(query, re.IGNORECASE)
    for doc_file in docs_dir.rglob("*.md"):
        try:
            lines = doc_file.read_text(encoding='utf-8').splitlines()
        except Exception:
            continue
        for idx, line in enumerate(lines):
            if pattern.search(line):
                results.append(f"{doc_file.relative_to(REPO_ROOT)}:{idx}: {line.strip()}")
    return results

@mcp.tool
def stop_sc4s():
   

@mcp.tool
def start_sc4s():
    pass

@mcp.tool
def restart_sc4s():
    pass

@mcp.tool
def set_env():
    pass

@mcp.tool
def add_parser():
    pass