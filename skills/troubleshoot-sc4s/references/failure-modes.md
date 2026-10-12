# SC4S failure modes

Choose the relevant symptom below and follow its direct command links. Use [runtime/path setup](operator-commands.md#runtime-and-paths) once, or the [Kubernetes/BYOE adaptation](operator-commands.md#kubernetes-and-byoe). Collect only the result needed to choose the next step. If chosen failure mode doesn't explain the issue, try another mode.

## Startup, unhealthy process, or repeated restart

1. Read [container status/logs](operator-commands.md#container-status-and-logs) or [systemd status/logs](operator-commands.md#systemd-status-and-logs). Find the first specific syntax, duplicate port/name, mount/access, or OOM error. For a running but unhealthy collector, use its [health endpoint](operator-commands.md#health-endpoint).
2. Follow the implicated error: [configuration validation](operator-commands.md#configuration-validation) for syntax, [listener ownership](operator-commands.md#listener-ownership) for port conflicts, or the [resource branch](#resource-pressure-delay-disk-growth-or-oom) for OOM/full storage. Inspect only the relevant recent change.
3. Correct the evidenced SC4S setting/file or restore its baseline. Verify the error stops, the process remains running, and relevant listeners/counters recover.

Docs: [startup and operations](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/).

## Missing events or growing queues

Read [counter trends](operator-commands.md#counter-trends) during affected traffic. Read [current logs](operator-commands.md#container-status-and-logs) if a failure needs explanation; a stopped collector leads to the [startup branch](#startup-unhealthy-process-or-repeated-restart).

| Observed trend | Next check |
| --- | --- |
| Source `processed` does not advance | [Listener/arrival branch](#one-senderprotocol-missing) |
| Source advances, HEC `processed` does not | [Parser/filter/routing branch](#fallback-parsing-or-missing-fields) or [metadata branch](#wrong-metadata-or-timestamp) |
| HEC `written` stalls, `queued` grows | [Outgoing HEC errors](#outgoing-hectls-error); correlate with [TCP backlog](operator-commands.md#tcp-backlog) only if transport stalls remain unclear |
| `dropped` increases | [Resource branch](#resource-pressure-delay-disk-growth-or-oom) and the current SC4S error; flag active loss |
| `written` advances, queue stays low or drains, drops unchanged | SC4S is forwarding/recovering; ask for affected-event visibility only if confirmation is needed |

If counters look healthy but visibility remains unresolved, report that limit and hand off; do not start Splunk searches/permission checks.

Docs: [statistics and TCP backpressure](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_resources/).

## Outgoing HEC/TLS error

Read [SC4S startup/current logs](operator-commands.md#container-status-and-logs) for `SC4S_ENV_CHECK_HEC`, `SC4S_ENV_CHECK_INDEX`, and the exact destination error/status. Then inspect the implicated [SC4S configuration excerpt](operator-commands.md#configuration-and-raw-sample): URL, token presence, TLS/CA mount, proxy, or index override.

| SC4S evidence | Action within scope |
| --- | --- |
| Wrong URL/path, absent local token, missing CA mount | Correct the evidenced SC4S setting/mount using the deployed release's docs |
| DNS/connect/timeout, certificate/hostname failure with correct SC4S settings | Hand off endpoint/error/time to the network or receiver owner |
| HTTP 401/403 or receiver token rejection | Check local token configuration/presence, then hand off receiver validation |
| `Incorrect index`, code 7 | Check the active SC4S index override for a typo; if intended, hand off to the receiver owner. One invalid index can reject a batch |
| Other 400 or 404 | Inspect the SC4S endpoint/template and exact error; do not assume every 400 is an index failure |
| 429/503 or proxy 502/504 with correct destination settings | Hand off downstream rejection/unavailability with the SC4S queue trend |

Keep diagnosis on the collector side; do not send direct HEC POST tests. After an SC4S correction, repeat [logs](operator-commands.md#container-status-and-logs) and [counter trends](operator-commands.md#counter-trends) to verify errors stop, writes advance, queues drain, and drops do not increase.

Docs: [HEC/token errors](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/#issue-hectoken-connection-errors-for-example-no-data-in-splunk), [SC4S destination variables](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#configure-your-splunk-hec-destination).

## One sender/protocol missing

1. Compare the affected [listener setting](operator-commands.md#configuration-and-raw-sample) with [listener ownership](operator-commands.md#listener-ownership). For bridge/pod deployments, use [published ports](operator-commands.md#container-port-mapping) or the relevant collector Service.
2. If needed, check [packet arrival](operator-commands.md#packet-arrival). No arrival: hand off to the sender/network owner. Arrival without processing: inspect SC4S's listener/protocol, inbound TLS settings, or [UDP receive errors](operator-commands.md#udp-receive-errors) when loss is suspected.
3. For TLS, use the collector handshake error and certificate/trust mounts; use the [TLS listener test](operator-commands.md#tls-listener-test) when negotiation remains unclear. Do not use plaintext replay. For a UDP warning, compare receive errors and requested versus kernel buffer sizes; hand off required host/kernel changes.
4. Verify progress from the affected path after a collector correction. Use [sample replay](operator-commands.md#sample-replay) only when requested/authorized; a local test does not verify the remote sender's path.

Docs: [listener/buffer/TLS validation](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/), [raw-message/arrival checks](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_resources/), and the affected [vendor source](https://splunk.github.io/splunk-connect-for-syslog/main/sources/).

## Fallback, parsing, or missing fields

1. Use one [raw message and affected parser excerpt](operator-commands.md#configuration-and-raw-sample) to compare format/header/framing with that release's vendor parser. Read relevant [parse errors](operator-commands.md#container-status-and-logs) or discarded counters only if needed; `>@<` marks the documented RFC error position.
2. Correct the smallest evidenced SC4S parser/filter/matching error. Reproduce a suspected built-in regression with the same release and sanitized sample. For a known noncompliant source, consult its documented `SC4S_DISABLE_DROP_INVALID_*` option rather than enabling broad exceptions.
3. Use [configuration validation](operator-commands.md#configuration-validation) and, when appropriate, [one-event replay](operator-commands.md#sample-replay); verify affected fields/metadata. If SC4S emits correct content and fields are missing only downstream, hand off to the Splunk owner.

Temporary debug/RAWMSG collection needs exact settings, duration, restart impact, capacity check, and restoration instructions.

Docs: [raw messages](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_resources/#obtain-raw-message-events), [noncompliant sources/debug](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/), and the affected [vendor source](https://splunk.github.io/splunk-connect-for-syslog/main/sources/).

## Wrong metadata or timestamp

1. Compare the reported event/metadata with deployed parser defaults. Use the [affected metadata/compliance/rewriter excerpt](operator-commands.md#configuration-and-raw-sample), including the actual `vendor_product` key.
2. For timestamp errors, inspect the raw offset and relevant SC4S timezone/parser setting. Prefer a source-scoped correction; a sender clock error belongs to its owner.
3. Apply the evidenced SC4S correction and verify a fresh affected sample plus an unaffected comparison when relevant. Correct collector output with downstream differences warrants a handoff; a new setting does not repair already indexed events.

Docs: [metadata and legacy timezones](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/), [timezone rewrites](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_resources/#fix-time-zones).

## Resource pressure, delay, disk growth, or OOM

1. Use the [ingestion decision table](#missing-events-or-growing-queues) to separate input, forwarding, backlog, and drops.
2. Select [CPU/RAM or disk/inode usage](operator-commands.md#resource-usage) for the reported symptom. For disk growth, inspect [buffer/alternate settings](operator-commands.md#configuration-and-raw-sample): `SC4S_DEST_GLOBAL_ALTERNATES` may enable `d_archive` / `d_hec_debug`. Use [archive/debug sizes](operator-commands.md#archive-and-debug-sizes) only if those destinations are enabled.
3. Propose a documented SC4S capacity/throughput change when evidence supports it. Hand off external capacity/network/storage faults; increasing workers is not a universal fix.
4. Verify restored headroom, writes, draining queues, and no new drops/OOM. Report known drops separately from backlog; already dropped events cannot be recovered from buffers.

Docs: [disk and UDP buffer issues](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/), [buffer variables](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/), [performance tuning](https://splunk.github.io/splunk-connect-for-syslog/main/architecture/fine-tuning/).
