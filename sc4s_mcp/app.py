from pathlib import Path

from fastmcp import FastMCP

from auth import build_auth_provider

ASYNC_JOB_TOOLS = (
    "set_env",
    "add_parser",
    "delete_parser",
    "set_splunk_metadata",
    "delete_splunk_metadata",
    "set_compliance_override",
    "delete_compliance_override",
)

SERVER_INSTRUCTIONS = f"""SC4S MCP safety rules apply to every tool call, including calls made outside a skill.
Before any mutation, read the affected live state, explain the exact change, show the final payload or diff,
and obtain fresh explicit user confirmation immediately before the call. Warn that set_env, set_splunk_metadata,
and set_compliance_override are full replacements.

Tools: {", ".join(ASYNC_JOB_TOOLS)}, return a job_id and require pooling with get_job_status.
Never claim success until the terminal status is success. All other tools are synchronous; do not call get_job_status for them.
Report failed jobs without retrying or rolling back automatically.
On a 409 conflict, poll the active job when possible, then re-read state, rebuild the preview,
and obtain fresh confirmation before retrying. After success, re-read the affected state and call sc4s_health;
report any verification or health failure clearly."""

mcp = FastMCP(
    "sc4s",
    auth=build_auth_provider(),
    instructions=SERVER_INSTRUCTIONS,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
