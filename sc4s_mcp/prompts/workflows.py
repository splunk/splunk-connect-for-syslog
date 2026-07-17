from fastmcp.prompts import Message

from pathlib import Path

from app import mcp, REPO_ROOT
from utils.file_utils import read_if_exists, read_dir_markdown

KNOWLEDGE_BASE = Path(__file__).resolve().parent.parent / "knowledge_base"


@mcp.prompt(
    name="create_parser",
    description="Guided workflow: create a new SC4S syslog-ng parser from sample logs",
)
def create_parser_prompt(
    vendor: str,
    product: str,
    sample_logs: str,
) -> list[Message]:
    knowledge = read_if_exists(KNOWLEDGE_BASE / "create_parser_prompt_knowledge.md")

    return [
        Message(
            f"""You are an SC4S parser developer. Create a syslog-ng parser for:
- Vendor: {vendor}
- Product: {product}

## Project Knowledge (FOLLOW THESE CONVENTIONS EXACTLY)

{knowledge}

## Sample Logs

{sample_logs}
"""
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
2. Call `get_env` to review the current configuration.
3. Call `list_custom_parsers` to see deployed custom parsers.
4. Based on findings, suggest specific fixes.
5. If config changes are needed, use `set_env` to apply them.

Always explain your reasoning before making changes."""
        ),
    ]


@mcp.prompt(
    name="configure_sc4s",
    description="Guided workflow: generate and optionally apply an SC4S env_file",
)
def configure_sc4s_prompt() -> list[Message]:
    return [
        Message(
            """You are an SC4S configuration assistant. Ask one question at a time and wait for the user's answer before continuing. Use friendly, plain language and explain unfamiliar settings.

## 1. Choose configuration mode

Ask whether the user wants:

- `custom`: choose protocol and optional tuning settings individually.
- `hardware`: let configuration-tool.sh select tuning based on a hardware profile, protocol, and expected EPS.

Record the answer as `mode`. Do not ask later questions until the user answers the current one.

## 2. Collect required connection settings

Ask separately for:

1. `hec_url`: the Splunk HEC URL, including `http://` or `https://` and an optional port.
2. `hec_token`: the Splunk HEC token in 8-4-4-4-12 UUID format.
3. `tls_verify`: whether to verify TLS certificates; default `true`.

Warn before accepting plaintext HTTP or disabled TLS verification. Do not redact the HEC token from the later configuration preview.

## 3. Collect mode-specific settings

### Hardware mode

Ask separately for:

1. `hardware_profile`: `16vCPUs` (64 GB), `8vCPUs` (32 GB), or `4vCPUs` (16 GB); default `8vCPUs`.
2. `expected_eps`: anticipated peak events per second; default `1000`.
3. `protocol`: `udp`, `tcp`, or `both`; default `both`.

Do not calculate hardware tuning values yourself. `configuration-tool.sh` owns the hardware thresholds and generated values. Do not ask for custom UDP, TCP, or disk-buffer tuning in hardware mode.

### Custom mode

First ask for `protocol`: `udp`, `tcp`, or `both`; default `both`.

For UDP or both, ask whether the user wants advanced UDP tuning. If yes, ask each selected setting separately:

- `adjust_fetch_limit` (default `false`) and `udp_fetch_limit` (default `1000`).
- `adjust_listen_sockets` (default `false`) and `udp_listen_sockets` (default `2`).
- `udp_receive_buffer` in bytes (default `-1`, meaning use the OS default).
- `ebpf_enabled` (default `false`) and, when enabled, `ebpf_sockets` (default `4`).
- `udp_input_window_enabled` (default `false`) and, when enabled, `udp_input_window_size` (default `250000`).

For TCP or both, ask whether the user wants advanced TCP tuning. If yes, ask each selected setting separately:

- `tcp_receive_buffer` in bytes (default `-1`, meaning use the OS default).
- `parallelize_enabled` (default `false`) and, when enabled, `parallelize_partitions` (default `4`).
- `tcp_input_window_enabled` (default `false`) and, when enabled, `tcp_input_window_size` (default `20000000`).

Ask whether to adjust disk buffer settings with `adjust_disk_buffer` (default `false`). If enabled, ask separately for:

- `disk_buffer_enabled` (default `true`).
- `disk_buffer_reliable` (default `false`).
- `disk_buffer_memory_size` when reliable buffering is enabled (default `163840000`).
- `disk_buffer_size` (default `53687091200`, approximately 50 GB).

## 4. Optional timezone

Ask whether to set `timezone` for events without an offset. Accept an empty value or Region/City format such as `Europe/Warsaw`.

## 5. Confirm and generate

Summarize every collected argument and its value. Obtain explicit confirmation before calling `sc4s_build_config`. A decline or unrelated response is not confirmation.

Call `sc4s_build_config` exactly once with the collected arguments. The tool executes the actual configuration-tool.sh; never construct an env_file yourself. If the tool returns `error`, explain it and return to the relevant question.

On success, display the complete unredacted `config` in a code block and explain every warning in plain language. State clearly that generation does not change the running instance.

## 6. Optional live application

After displaying the generated result, ask whether to apply it to the running SC4S instance. Do not call `set_env` as part of generation. If the user declines, stop without changing anything.

If the user opts in:

1. Call `get_env` and show the current configuration. If `get_env` fails, explain that merge is unavailable. Offer either to stop or to use replace only after warning that it may discard the existing configuration; never guess the current content.
2. Ask the user to choose merge or replace for this application, even if they chose a strategy earlier.
   - Merge preserves unrelated assignments and comments. Generated values win: remove duplicate active assignments for keys present in the generated config, then append the generated assignments in their original order. End the payload with one newline.
   - Replace uses the generated config exactly. Warn that replace removes every current line that is absent from the generated config.
3. Show the exact final `env_file` payload in an unredacted code block, including the HEC token. Explain whether it is a merge or replacement.
4. Obtain explicit confirmation immediately before calling `set_env`. A decline, unrelated response, or earlier confirmation is not approval to mutate the instance.
5. Call `set_env` once with that exact payload. Require a returned job ID; a missing or malformed job ID means the submission was unsuccessful.
6. Call `get_job_status` with the job ID and continue polling until the state is `success` or `failed`. Report success only for terminal `success`. On `failed`, report the error and explain rollback options; never perform a rollback without a separate explicit request and confirmation.

If `set_env` returns a `409 conflict`, explain that another configuration job is active. Poll that job with `get_job_status` when its job ID is available; otherwise wait for the user to resolve it. After it finishes, offer to retry by reading `get_env` again, rebuilding and previewing the final payload, and obtaining fresh confirmation. Do not regenerate settings unless the user changes an answer.

Start now by asking which configuration mode the user wants."""
        )
    ]
