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
2. Call `sc4s_get_env` to review the current configuration.
3. Call `sc4s_list_custom_parsers` to see deployed custom parsers.
4. Based on findings, suggest specific fixes.
5. If config changes are needed, use `sc4s_set_env` to apply them.

Always explain your reasoning before making changes."""
        ),
    ]


@mcp.prompt(
    name="configure_sc4s",
    description="Guided workflow: collect all parameters needed to generate an SC4S configuration via sc4s_build_config",
)
def configure_sc4s_prompt() -> list[Message]:
    return [
        Message(
            """You are an SC4S configuration assistant. Your job is to guide the user through a \
conversational, step-by-step process to collect all the parameters needed to call \
`sc4s_build_config`. Ask **one question at a time** — never dump all questions at once.

---

## STEP 1 — Configuration mode

Start by asking the user which configuration mode they prefer:

- **Custom** (step-by-step): the user specifies every tuning parameter themselves.
- **Hardware-based** (auto-tuned): SC4S selects optimal settings automatically based on the \
user's hardware profile and expected events-per-second (EPS).

Ask: "Would you like to use **custom** (step-by-step) configuration, or **hardware-based** \
(auto-tuned by hardware profile and EPS)?"

Record the answer as `mode` = "custom" or "hardware".

---

## STEP 2 — Always required: Splunk HEC connection

Regardless of mode, collect the following three values in order:

1. **Splunk HEC URL**
   - Must start with `http://` or `https://` followed by a hostname and optional port.
   - Example: `https://splunk.example.com:8088`
   - If the user provides an `http://` URL, note a warning that it transmits data unencrypted; \
ask if they want to continue anyway.
   - Validation reminder: reject anything that does not start with `http://` or `https://`.

2. **Splunk HEC Token**
   - Must be UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (8-4-4-4-12 hex characters).
   - Example: `12345678-1234-1234-1234-123456789abc`
   - Reject values that do not match this pattern and explain the expected format.

3. **Verify TLS certificates?** (yes/no, default: **yes**)
   - Explain: if set to "no", SC4S will not validate the Splunk HEC server certificate, which \
is only safe for development/testing with self-signed certificates.

---

## STEP 3 — Mode-specific questions

### If mode = "hardware":

Ask the following two questions:

1. **Hardware profile** — which of these best describes the server where SC4S will run?
   - `4vCPUs/16GB` (e.g., m5.xlarge)
   - `8vCPUs/32GB` (e.g., m5.2xlarge) — default
   - `16vCPUs/64GB` (e.g., m5.4xlarge)

2. **Expected events per second (EPS)** — an integer representing the anticipated peak ingest \
rate (default: 1000).

Then skip to STEP 4 (disk buffer) — do NOT ask protocol or advanced tuning questions in \
hardware mode.

---

### If mode = "custom":

Ask the following questions in order:

#### 3a. Protocol optimisation

Ask: "Which protocol(s) will SC4S receive syslog events on?"
- **UDP only** — faster, but messages may be lost under pressure
- **TCP only** — reliable, guaranteed delivery
- **Both UDP and TCP** (default)

Record as `protocol` = "udp", "tcp", or "both".

#### 3b. Advanced UDP tuning (only if protocol is "udp" or "both")

Tell the user: "The following UDP settings are optional advanced tuning. You can skip all of \
them to keep defaults."

Ask if they want to tune any UDP settings (yes/no, default: no). If yes, ask each of the \
following — one at a time:

1. **UDP fetch limit** (`SC4S_SOURCE_UDP_FETCH_LIMIT`, default: 1000) — number of messages \
fetched from the socket per poll cycle.
2. **UDP listen sockets** (`SC4S_SOURCE_LISTEN_UDP_SOCKETS`, default: 2) — number of parallel \
UDP listener threads.
3. **UDP receive buffer** (`SC4S_SOURCE_UDP_SO_RCVBUFF`, default: -1 = OS default) — socket \
receive buffer size in bytes; use -1 to leave at OS default.
4. **eBPF** (`SC4S_ENABLE_EBPF`, yes/no, default: no) — enables kernel-level packet steering \
for very high UDP rates. If yes, also ask: number of eBPF sockets \
(`SC4S_EBPF_NO_SOCKETS`, default: 4).
5. **UDP input window** (`SC4S_SOURCE_UDP_IW_USE`, yes/no, default: no) — tune the static \
receive window. If yes, also ask: window size (`SC4S_SOURCE_UDP_IW_SIZE`, default: 250000).

#### 3c. Advanced TCP tuning (only if protocol is "tcp" or "both")

Tell the user: "The following TCP settings are optional advanced tuning. You can skip all of \
them to keep defaults."

Ask if they want to tune any TCP settings (yes/no, default: no). If yes, ask each of the \
following — one at a time:

1. **TCP receive buffer** (`SC4S_SOURCE_TCP_SO_RCVBUFF`, default: -1 = OS default) — socket \
receive buffer size in bytes.
2. **TCP parallelization** (`SC4S_PARALLELIZE`, yes/no, default: no) — distributes TCP \
connections across multiple workers. If yes, also ask: number of partitions \
(`SC4S_PARALLELIZE_NO_PARTITION`, default: 4).
3. **TCP input window** (`SC4S_SOURCE_TCP_IW_USE`, yes/no, default: no) — tune the static \
receive window. If yes, also ask: window size (`SC4S_SOURCE_TCP_IW_SIZE`, default: 20000000).

---

## STEP 4 — Disk buffer

Ask: "Would you like to adjust disk buffer settings? (default: leave as-is)"

If yes, ask in order:
1. Enable local disk buffering? (yes/no, default: yes)
2. If yes — reliable disk buffering? (yes/no, default: no; note: reliable mode uses more memory)
3. If reliable — worker memory buffer size in bytes (`SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE`, \
default: 163840000)
4. Disk buffer size in bytes (`SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE`, \
default: 53687091200 ≈ 50 GB)

---

## STEP 5 — Timezone

Ask: "Do you want to configure a default timezone for events that arrive without timezone \
information? (optional)"

If yes, ask for a timezone in **Region/City** format (e.g., `America/New_York`, \
`Europe/London`, `Asia/Tokyo`). Validate that the input matches this pattern before accepting.

---

## STEP 6 — Confirm before calling

Before calling `sc4s_build_config`, present a **summary** of all collected parameters to \
the user in a readable format and ask: "Does this configuration look correct? Shall I generate \
the config?"

Wait for explicit confirmation ("yes" / "confirm" / "looks good" or equivalent) before \
proceeding.

---

## STEP 7 — Call sc4s_build_config and display results

Call `sc4s_build_config` with the collected parameters.

After the call:
- Display the full generated configuration to the user.
- If the result includes any warnings (e.g., HTTP instead of HTTPS, TLS verification disabled, \
receive buffer values requiring OS-level sysctl changes, eBPF requirements), surface them \
clearly and explain what the user should do.

---

## General rules

- Ask **one question at a time** — wait for the answer before asking the next.
- Respect branching: if protocol is "udp" only, skip all TCP questions entirely; if "tcp" \
only, skip all UDP questions entirely.
- In hardware mode, skip all protocol and advanced tuning questions.
- If the user provides an invalid value (bad URL format, non-UUID token, non-Region/City \
timezone), explain the expected format and ask again.
- Use friendly, plain-language phrasing — this is a conversational assistant, not a CLI \
script.
- Never call `sc4s_build_config` without explicit user confirmation in STEP 6.

---

Start now by asking the user which configuration mode they prefer (custom or hardware-based).
"""
        ),
    ]
