from fastmcp.prompts import Message

from app import mcp, REPO_ROOT
from utils.file_utils import read_dir_markdown

PARSER_CREATOR_DIR = REPO_ROOT / "skills" / "parser-creator"


@mcp.prompt(
    name="create_parser",
    description="Guided workflow: create a new SC4S syslog-ng parser from sample logs",
)
def create_parser_prompt(
    vendor: str,
    product: str,
    sample_logs: str,
) -> list[Message]:
    sections = []
    for filename in ("SKILL.md", "parser-guide.md"):
        content = (PARSER_CREATOR_DIR / filename).read_text(encoding="utf-8")
        if not content.strip():
            raise RuntimeError(f"Parser creation knowledge is empty: {filename}")
        sections.append(f"### {filename}\n\n{content}")
    knowledge = "\n\n".join(sections)

    return [
        Message(f"""You are an SC4S parser developer. Create a syslog-ng parser for:
- Vendor: {vendor}
- Product: {product}

## Project Knowledge (FOLLOW THESE CONVENTIONS EXACTLY)

The parser-creator workflow and its referenced parser guide are embedded below.

{knowledge}

## Sample Logs

{sample_logs}
"""),
    ]


@mcp.prompt(
    name="troubleshoot_sc4s",
    description="Guided workflow: diagnose and fix SC4S issues",
)
def troubleshoot_prompt(symptom: str) -> list[Message]:
    ts_content = read_dir_markdown(REPO_ROOT / "docs" / "troubleshooting")

    return [
        Message(f"""You are an SC4S troubleshooting expert.

## Problem Description
{symptom}

## SC4S Troubleshooting Knowledge
{ts_content}

## Diagnostic Steps
1. First call `sc4s_health` to check the instance status.
2. Call `get_env` to review the current configuration.
3. Call `list_custom_parsers` to see deployed custom parsers.
4. Based on findings, suggest specific fixes.
5. If config changes are needed, use `set_env` to apply them.

Always explain your reasoning before making changes."""),
    ]
