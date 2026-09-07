---
name: sc4s-guided-configuration
description: Use when users ask to configure SC4S, create an env_file, set Splunk HEC details, tune performance, or apply generated settings to a running SC4S instance through natural conversation.
---

# SC4S Configurator

## Core rules

This workflow guides the user through generating and optionally applying an
SC4S `env_file` based on their requirements.
It uses MCP tool whose name ends with `sc4s_build_config`.
Use the same namespace prefix for `get_env`, `set_env`, and `get_job_status`.

Call `sc4s_build_config` with one `config` object. Populate it from the
tool's exposed schema. The schema exposes actual SC4S environment
variables with their uppercase `SC4S_*` names, while non-environment tool
arguments retain their lowercase names (for example `protocol`, `mode`,
`hardware`, `expectedEps`, and `adjust_fetch_limit`).

Whenever asking a configuration question, first give a short explanation of
what the setting controls, the main trade-off, and a relevant SC4S
documentation link. For optional scalar settings, do not ask a separate
"do you want to adjust it?" question followed by a value question. Ask once
whether to keep the default or change it, include the default value and units in
that same question, and treat a supplied value as opting into the setting.
Ask a follow-up question only when a value depends on a preceding enable/disable
choice. After a valid answer, acknowledge it briefly and continue without
repeating the full explanation or searching the documentation again. If the user
asks an additional question, answer it. Use only SC4S documentation as source of
truth; if you cannot find an answer, say so.

## 1. Start the guided workflow

Begin every new configuration workflow with this short message, then ask
the mode question as the only question in that message:

> I’ll guide you through creating an SC4S `env_file` for your Splunk HEC
> destination and log traffic. We’ll choose either automatic hardware-based
> tuning or custom tuning, review the generated configuration together, and
> only apply it to a running SC4S instance if you explicitly choose to do so.

Do not ask for HEC details or tuning values in the opening message.

## 2. Choose mode

Explain that user has to choose the configuration mode for the configuration tool:

- `custom`: choose protocol and optional tuning individually.
- `hardware`: let the configuration tool choose settings based on hardware, protocol, and expected EPS.

Store `custom` as `mode="1"` and `hardware` as `mode="2"` in `config`.

Link to the [SC4S
configuration modes](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/configuration-tool/#configuration-modes).

## 3. Collect the Splunk connection

Explain that the HEC URL identifies where SC4S sends events, the token
authenticates SC4S to HEC, and TLS verification protects the connection from
untrusted certificates. Disabling verification or using HTTP weakens security
and should be limited to trusted or temporary environments. Link to [SC4S HEC
configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-splunk-hec-destination).

Ask separately for:

1. `SC4S_HEC_URL`: the HEC destination URL, including `http://` or `https://` and
   an optional port.
2. `SC4S_HEC_TOKEN`: the UUID-form HEC credential that authorizes SC4S to send
   events.
3. `SC4S_TLS_VERIFY`: whether SC4S validates the HEC server certificate; keep
   `true` unless a trusted self-signed setup requires otherwise. Default
   `true`.

Warn before accepting plaintext HTTP or disabled TLS verification. Later previews are intentionally unredacted, including the HEC token.

## 4. Collect mode-specific settings

### Hardware mode

Explain that the hardware profile selects the closest predefined CPU/RAM
profile for automatic tuning, while expected EPS should be the anticipated
peak throughput rather than the average. The protocol choice determines the
transport trade-off: UDP favors throughput but can lose packets under load,
TCP provides ordered reliable delivery, and `both` supports both sources.
Link to [hardware profiles](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/configuration-tool/#hardware-profiles)
and [protocol selection](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/configuration-tool/#protocol-selection).

Ask separately for:

1. `hardware`: the closest CPU/RAM profile used by the script to
   select automatic tuning. Offer `16vCPUs` (64GB RAM), `8vCPUs` (32GB RAM),
   or `4vCPUs` (16GB RAM); default to `8vCPUs`. Store and pass only the raw
   value (`16vCPUs`, `8vCPUs`, or `4vCPUs`).
2. `expectedEps`: the anticipated peak events per second used by the script
   when selecting hardware thresholds; default `1000`.
3. `protocol`: the input transport—UDP favors throughput but may lose packets
   under load, TCP provides ordered reliable delivery, and `both` supports
   both; default `both`.

Do not ask for custom UDP, TCP, or disk-buffer tuning in hardware mode.

### Custom mode

Explain that custom mode is for users who need to override individual tuning
values; the advanced settings can increase CPU, memory, kernel-buffer, or disk
requirements. Link to [SC4S advanced configuration
options](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/configuration-tool/#advanced-options)
and the [SC4S fine-tuning guide](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/).

Ask for `protocol`: `udp`, `tcp`, or `both`; explain the same throughput versus
reliability trade-off described above. Link to [protocol
selection](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/configuration-tool/#protocol-selection).
Default `both`.

For UDP or both, explain that these settings affect how UDP traffic is read
from the kernel and buffered in syslog-ng. Higher values can improve burst
handling but consume more CPU or memory and can increase latency. Ask for each
option in one compact question:

- `SC4S_SOURCE_UDP_FETCH_LIMIT`: explain that fetch limit controls the maximum number of messages read
  in one operation; too low underuses the buffer, while too high can fill it too quickly.
  Ask: keep the default `1000` messages per operation, or provide a different
  value? When supplied, set `adjust_fetch_limit=true` and set
  `SC4S_SOURCE_UDP_FETCH_LIMIT`. Link to [SC4S fetch-limit
  guidance](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#fetch-limit).
- `SC4S_SOURCE_LISTEN_UDP_SOCKETS`: explain that multiple UDP sockets can distribute traffic
  across CPU threads; more sockets are not automatically better. Ask: keep the
  default `4` sockets, or provide a different value? Pass only a supplied value
  by setting `adjust_listen_sockets=true` and
  `SC4S_SOURCE_LISTEN_UDP_SOCKETS`. Link to [SC4S UDP socket
  tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#increase-the-number-of-udp-sockets).
- `SC4S_SOURCE_UDP_SO_RCVBUFF`: the kernel-side UDP receive buffer that absorbs short
  bursts before SC4S processes them; larger values also require suitable OS
  limits. Warn about the OS-kernel dependency, then ask: keep the OS default
  `-1`, or provide a buffer size in bytes? Link to [SC4S receive-buffer
  tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#tune-the-receiving-buffer).
- `SC4S_ENABLE_EBPF` and `SC4S_EBPF_NO_SOCKETS`: before asking, warn that eBPF requires
  host support and a privileged SC4S container; otherwise SC4S may fail to
  start or eBPF may not work correctly. Ask in one question: leave eBPF
  disabled, or enable it with how many sockets? The default is `false`, and
  the default socket count when enabled is `4`. Link to [SC4S eBPF
  tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#enable-ebpf).
- UDP input window: whether to add an application-level UDP buffer for slow
  outputs; it can reduce transient loss but increases memory use and latency.
  Ask whether to keep the default disabled or enable it. When enabled, ask
  whether to keep the default `250000` messages or provide a different size.
  Record the answers as `SC4S_SOURCE_UDP_IW_USE` and
  `SC4S_SOURCE_UDP_IW_SIZE`; do not expose those names in the conversation.
  Link to [SC4S input-window
  tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#tune-static-input-window-size).

When UDP input-window tuning is enabled, enforce the effective fetch limit
(`1000` when `SC4S_SOURCE_UDP_FETCH_LIMIT` is unset) <=
`SC4S_SOURCE_UDP_IW_SIZE`. If the
fetch limit is larger, warn the user that one read could fill or overrun the
application buffer, ask them to lower the fetch limit or increase the
input-window size, and do not generate the configuration until the values
satisfy the relationship. Link to the
[SC4S fetch-limit guidance](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#fetch-limit).

Before accepting a non-default `SC4S_SOURCE_UDP_SO_RCVBUFF` or
`SC4S_SOURCE_TCP_SO_RCVBUFF`,
warn that the SC4S setting must be supported by the host OS kernel limits. The
user must align the SC4S value with the relevant OS receive-buffer settings;
otherwise the value may be ineffective, cause degraded behavior, or prevent
SC4S from starting correctly. Link to [SC4S receive-buffer tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#tune-the-receiving-buffer).

For TCP or both, explain that these settings control kernel receive buffering
and application-level concurrency/buffering. They can improve throughput but
increase memory or CPU consumption. Ask each setting compactly:

- `SC4S_SOURCE_TCP_SO_RCVBUFF`: the kernel-side TCP receive buffer for bursts; larger
  values require suitable OS limits. Warn about the OS-kernel dependency, then
  ask: keep the OS default `-1`, or provide a buffer size in bytes? Link to
  [SC4S receive-buffer tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#tune-the-receiving-buffer).
- `SC4S_PARALLELIZE` and `SC4S_PARALLELIZE_NO_PARTITION`: explain that TCP
  parallelization splits processing across partitions and can improve
  throughput at additional CPU cost. Ask in one question: leave it disabled,
  or enable it with how many partitions? The defaults are `false` and `4`,
  respectively. SC4S supports at most `32` workers. If the user enters more
  than `32`, warn them and require a corrected value from `1` through `32`; do
  not silently clamp or pass the invalid value to the tool. Link to [SC4S
  parallelize TCP processing](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#parallelize-tcp-processing).
- TCP input-window size: SC4S already enables this application-level buffer by
  default. Larger windows use more memory and can add latency. Ask whether to
  keep the default `20000000` messages or provide a different size. When the
  user supplies a size, set `customize_tcp_input_window_size=true` and record
  it in `config`. Link to [SC4S input-window
  tuning](https://splunk.github.io/splunk-connect-for-syslog/develop/architecture/fine-tuning/#tune-static-input-window-size).

Explain that disk buffering protects against temporary HEC or network outages
by storing events locally, but consumes persistent disk space. Reliable
buffering survives restarts more strongly but has a performance cost; normal
buffering is the recommended default for most deployments. Link to [SC4S disk
buffer configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-sc4s-disk-buffer).

Ask: keep the default disk-buffer behavior, or customize it? The default is
`false` for customization. When the user keeps the default, leave all
disk-buffer settings untouched. When they choose to customize it, set
`adjust_disk_buffer=true` and ask:

- `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE`: whether local disk buffering is active. Default
  `true`. If the user disables it, do not ask about the dependent disk-buffer
  settings below. Link to [SC4S disk-buffer
  configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-sc4s-disk-buffer).
- `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE`: whether to use the more durable reliable queue mode;
  it offers stronger restart/crash protection at a performance cost. Ask
  whether to keep the default `false` or enable it. Link to [SC4S disk-buffer
  configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-sc4s-disk-buffer).
- `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE`: memory reserved per worker for reliable buffering;
  larger values increase memory use. Ask only when reliable buffering is
  enabled: keep the default `163840000` bytes per worker, or provide a different
  value. Link to [SC4S disk-buffer
  configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-sc4s-disk-buffer).
- `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE`: maximum local disk space allocated per worker for queued
  events. Ask only when disk buffering is enabled: keep the default
  `53687091200` bytes (approximately 50 GB) per worker, or provide a different
  value. Link to [SC4S disk-buffer
  configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-your-sc4s-disk-buffer).

## 5. Optional timezone

Explain that this applies only to events that do not contain a timezone offset;
it does not change timestamps that already include one. Link to [SC4S
timezone configuration](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/#configure-timezones-for-legacy-sources).

Ask one compact question: leave `SC4S_DEFAULT_TIMEZONE` unset, or provide a Region/City
value such as `Europe/Warsaw`? An empty answer keeps the default unset.

## 6. Confirm and generate

Before generation, give one concise, human-readable summary. Group the
settings instead of listing every script or environment variable:

- Connection: HEC destination, TLS verification, and whether the token was
  provided. Do not repeat the token in the summary.
- Mode and traffic: hardware/custom mode, expected peak EPS when applicable,
  and protocol.
- UDP: only the non-default fetch limit, socket count, receive buffer, eBPF
  state/socket count, and input-window state/size.
- TCP: only the non-default receive buffer, parallelization state/partition
  count, and input-window state/size.
- Disk buffering: whether customization was requested, whether buffering is
  enabled, reliable mode, and any custom memory/disk sizes.
- Timezone: the selected timezone or “unset.”

For values left at defaults, say “remaining at the SC4S default” instead of
printing their internal variable names. Prefer short “Selected changes” and
“Defaults left unchanged” sections. Present only relevant warnings and
trade-offs. Do not repeat the full explanations already given for each option.

Explain that the official SC4S configuration script now receives these selected
settings and resolves its defaults/automatic tuning to render the exact
`env_file` preview. Generation does not modify or restart the running SC4S
instance. Obtain explicit confirmation before calling `sc4s_build_config`; a
decline or unrelated response is not confirmation.

Call `sc4s_build_config` exactly once with the collected values nested in its
`config` object. On `error`, explain it and return to the relevant question.

On success, display the complete script-generated `config` in a code block and
explain every warning. Do not create a second variable-by-variable summary of
the generated file. State that generation does not change the running
instance.

## 7. Optional live application

After the generated preview, ask whether to apply it. If the user declines, stop without mutation.

Explain that generation only creates a preview, while applying writes the
selected `env_file` to SC4S and restarts the runtime. Link to the [SC4S
configuration reference](https://splunk.github.io/splunk-connect-for-syslog/latest/configuration/).

If the user opts in:

1. Call `get_env` and show the current configuration. If it returns HTTP 404,
   explain that the SC4S management API is disabled and requires
   `SC4S_API_MANAGEMENT_ENABLED=true` followed by a runtime restart; stop
   instead of offering replace. For other failures, explain that merge is
   unavailable and offer to stop or use replace only after warning that current
   content may be discarded. Never guess current content.
2. Inspect the current active assignments. If
   `SC4S_API_MANAGEMENT_ENABLED=true` is present and the generated preview does
   not include it, explain that it keeps the SC4S management API available
   after a full runtime restart. Ask whether to preserve it; recommend yes.
   When the user chooses yes, carry that assignment into the final merged
   payload. If they decline, warn that the API connection can be lost after a
   full runtime restart and require fresh explicit confirmation before applying.
3. Explain that merge keeps unrelated existing settings and comments, while
   replace uses only the generated file and removes current lines not present
   in it. Ask the user to choose merge or replace for this application.
   - Merge preserves unrelated assignments and comments. Generated values win:
     remove duplicate active assignments for generated keys, then append
     generated assignments in their original order. Preserve the management API
     assignment when the user selected preservation. End with one newline.
   - Replace uses the generated config exactly. Warn that replace removes every
     current line absent from the generated config, including the management API
     assignment unless it is explicitly present in the replacement payload.
4. Show the exact final `env_file` payload in an unredacted code block, including the HEC token, and explain the selected strategy.
5. Obtain explicit confirmation immediately before calling `set_env`. A decline, unrelated response, or earlier approval is not mutation confirmation.
6. Call `set_env` once with that exact payload. Treat a missing or malformed job ID as an unsuccessful submission.
7. Call `get_job_status` with the job ID and poll until `success` or `failed`. Report success only for terminal `success`. On `failed`, report the error and explain rollback options; never roll back without a separate explicit request and confirmation.

If `set_env` returns a `409 conflict`, explain that another configuration job is active. Poll it when its job ID is available; otherwise wait for the operator to resolve it. After completion, offer a retry: call `get_env` again, rebuild and preview the final payload, and obtain fresh confirmation. Do not regenerate settings unless an answer changes.
