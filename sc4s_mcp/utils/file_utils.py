from pathlib import Path


def read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_dir_markdown(directory: Path) -> str:
    if not directory.exists():
        return ""
    sections = []
    for f in sorted(directory.glob("*.md")):
        sections.append(f.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(sections)
