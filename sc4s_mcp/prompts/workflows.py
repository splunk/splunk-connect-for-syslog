from fastmcp.prompts import Message

from app import mcp, REPO_ROOT
from utils.file_utils import read_if_exists, read_dir_markdown

SKILL_PATH = REPO_ROOT / ".agents" / "skills" / "parser-creator" / "SKILL.md"
TESTING_PATH = (
    REPO_ROOT / ".agents" / "skills" / "parser-creator" / "references" / "testing-parsers.md"
)


@mcp.prompt(
    name="create_parser",
    description="Guided workflow: create a new SC4S syslog-ng parser from sample logs",
)
def create_parser_prompt(
    vendor: str,
    product: str,
    sample_logs: str,
) -> list[Message]:
    skill_text = read_if_exists(SKILL_PATH)
    testing_text = read_if_exists(TESTING_PATH)

    return [
        Message(
            f"""You are an SC4S parser developer. Create a syslog-ng parser for:
- Vendor: {vendor}
- Product: {product}

## Project Knowledge (FOLLOW THESE CONVENTIONS EXACTLY)

{skill_text}

## Testing Reference

{testing_text}

## Sample Logs

{sample_logs}

## Workflow Steps

1. Analyze the sample logs -- identify the message format, key fields, and unique \
identifiers for filtering.
2. Create the filter -- use the project knowledge above as reference for filter syntax.
3. Create the parser -- follow the naming conventions from the guide above.
4. Generate unit tests -- use the testing reference above.
5. Use `sc4s_add_parser` tool to deploy the parser to a running SC4S instance.
6. Validate -- call `sc4s_health` to confirm SC4S is still healthy after adding the parser.

IMPORTANT: Follow the naming conventions and file structure from the Project Knowledge \
section exactly. Do not invent your own conventions."""
        ),
    ]


@mcp.prompt(
    name="troubleshoot_sc4s",
    description="Guided workflow: diagnose and fix SC4S issues",
)
def troubleshoot_prompt(symptom: str) -> list[Message]:
    ts_content = read_dir_markdown(REPO_ROOT / "docs" / "troubleshooting")

    return [
        Message(
            f"""You are an SC4S troubleshooting expert.

## Problem Description
{symptom}

## SC4S Troubleshooting Knowledge
{ts_content}

## Diagnostic Steps
1. First call `sc4s_health` to check the instance status.
2. Call `sc4s_get_env` to review the current configuration.
3. Call `sc4s_list_custom_parsers` to see deployed custom parsers.
4. Based on findings, suggest specific fixes.
5. If config changes are needed, use `sc4s_set_env` to apply them.

Always explain your reasoning before making changes."""
        ),
    ]