#!/usr/bin/env python3
"""Regenerate the Sources navigation in mkdocs.yml from the docs/sources tree.

Zensical does not expand a directory referenced in ``nav`` the way the old
mkdocs-include-dir-to-nav plugin did, so the "Message Formats" and "Known
Vendors" entries must list their pages explicitly. Run this after adding or
removing source docs:

    python docs/gen_sources_nav.py

Only the lines between the AUTOGEN markers in mkdocs.yml are rewritten; page
titles are left to Zensical, which derives them from each page's H1.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MKDOCS = REPO / "mkdocs.yml"
DOCS = REPO / "docs"
SOURCES = DOCS / "sources"


def _rel(path: Path) -> str:
    return path.relative_to(DOCS).as_posix()


def _base_block() -> list[str]:
    return [f'- "{_rel(md)}"' for md in sorted((SOURCES / "base").glob("*.md"))]


def _vendor_files(vendor: Path) -> list[Path]:
    mds = sorted(vendor.glob("*.md"), key=lambda p: p.name.lower())
    mds.sort(key=lambda p: p.name != "index.md")  # index.md first, if present
    return mds


def _vendor_block() -> list[str]:
    vendors = sorted(
        (d for d in (SOURCES / "vendor").iterdir() if d.is_dir()),
        key=lambda d: d.name.lower(),
    )
    lines: list[str] = []
    for vendor in vendors:
        mds = _vendor_files(vendor)
        if not mds:
            continue
        if len(mds) == 1:
            lines.append(f'- {vendor.name}: "{_rel(mds[0])}"')
        else:
            lines.append(f"- {vendor.name}:")
            lines.extend(f'    - "{_rel(md)}"' for md in mds)
    return lines


def _replace_block(text: str, tag: str, block: list[str]) -> str:
    begin = f"# <<< AUTOGEN:{tag} >>>"
    end = f"# <<< /AUTOGEN:{tag} >>>"
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if line.strip() == begin:
            indent = line[: len(line) - len(line.lstrip())]
            out.extend(f"{indent}{entry}" for entry in block)
            i += 1
            while i < len(lines) and lines[i].strip() != end:
                i += 1
            if i >= len(lines):
                raise SystemExit(f"mkdocs.yml: missing '{end}'")
            out.append(lines[i])
            replaced = True
        i += 1
    if not replaced:
        raise SystemExit(f"mkdocs.yml: missing '{begin}'")
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def main() -> None:
    text = MKDOCS.read_text()
    text = _replace_block(text, "base", _base_block())
    text = _replace_block(text, "vendor", _vendor_block())
    MKDOCS.write_text(text)
    print("mkdocs.yml Sources nav regenerated from docs/sources/")


if __name__ == "__main__":
    main()
