from app import mcp, REPO_ROOT

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
            sections.append(filepath.read_text())
    return "\n\n---\n\n".join(sections)
