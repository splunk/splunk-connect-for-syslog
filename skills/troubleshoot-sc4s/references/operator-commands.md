# SC4S operator commands

Use the check linked from [failure modes](failure-modes.md). Read the setup below, then only the selected command section. Diagnostic decisions and follow-up routing belong in failure modes.

## Runtime and paths

Run container commands on the collector host with the account/runtime that owns SC4S. Set these variables before using a command that references them:

```bash
RUNTIME=podman                        # or docker
CONTAINER=SC4S                       # actual collector name
```

For rootless deployments, omit `sudo` and use the service account. Substitute actual ports, mounts, and incident windows for the examples. For pods or non-container installations, use [Kubernetes and BYOE](#kubernetes-and-byoe).

## Container status and logs

Check the collector state and the first specific startup/delivery error:

```bash
sudo "$RUNTIME" inspect --format '{{json .State}}' "$CONTAINER"
sudo "$RUNTIME" logs --since 15m --timestamps --tail 100 "$CONTAINER"
```

Use the failure/startup window instead of `15m` when needed. Return the state and first relevant error with nearby lines. Look for syntax errors, port conflicts, OOM, and `SC4S_ENV_CHECK_HEC` / `SC4S_ENV_CHECK_INDEX`. The startup markers record SC4S's HEC/index checks at startup, not current delivery.

## Systemd status and logs

Use when systemd owns SC4S or its automatically removed container is gone:

```bash
sudo systemctl status sc4s --no-pager -l
sudo journalctl -b -u sc4s --no-pager -o short-iso -n 100
```

Substitute the actual service name. Return the first specific error with nearby lines; a generic systemd failure is insufficient.

## Version

For release-dependent advice, use the startup `sc4s version=...` line. If unavailable and the collector is running:

```bash
sudo "$RUNTIME" exec "$CONTAINER" cat /etc/syslog-ng/VERSION
```

Return the SC4S release.

## Health endpoint

Check the collector's exposed health/API endpoint:

```bash
curl --connect-timeout 5 --max-time 10 -sS -i http://127.0.0.1:8080/health
```

Use the actual collector API address/scheme/port and trusted CA for TLS. Return HTTP status/body or the connection error. A host-network address may not reach a bridge container/pod. HTTP 200 alone does not prove delivery; this is the SC4S endpoint, not HEC health.

## Counter trends

Measure receiving, routing, and forwarding while affected traffic is expected. Run twice about 30 seconds apart and return both timestamps and matching active rows:

```bash
date -u
sudo "$RUNTIME" exec "$CONTAINER" syslog-ng-ctl stats \
  | grep -E '(^src\..*;(processed|connections);|d_hec.*;(processed|written|queued|dropped|memory_usage);)'
```

Ignore orphaned state `o` rows; active rows use `a`. Do not compare across restarts or reset counters. Missing optional counters or different component names are not proof of failure; request the affected component's unfiltered rows only when necessary. `processed` alone does not prove delivery; shared source counters do not prove receipt from one particular sender. Use the [ingestion decision table](failure-modes.md#missing-events-or-growing-queues) to choose the next check.

## Listener ownership

Check whether syslog-ng owns the affected listener, or whether the port is absent or owned by another process. On a standard host-network deployment, substitute the actual port and choose one protocol:

```bash
sudo ss -lunp 'sport = :514'           # UDP
sudo ss -ltnp 'sport = :514'           # TCP
```

Expected: syslog-ng owns that port. Return only the matching row or state that none exists. For bridge containers/pods, host sockets alone may not expose the listener; use the relevant published port/Service.

## Container port mapping

For a bridge-network container, check the published listener port/protocol:

```bash
sudo "$RUNTIME" port "$CONTAINER"
```

Return only the affected mapping or state that it is absent. Host-network containers do not need published mappings.

## TLS listener test

When inbound TLS negotiation is in question, use the [documented listener test](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/#issue-invalid-sc4s-tls-listener). Run on the Linux collector host or a Linux test host that can reach the collector's TLS listener:

```bash
sudo "$RUNTIME" run --rm -ti --network host docker.io/drwetter/testssl.sh \
  --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

Replace the IP, certificate FQDN, and TLS port with the affected listener's values. Host networking lets the test container reach a host listener at `127.0.0.1`; for bridge containers or pods, use the reachable published port or Service address. This starts a testssl.sh client, with no SC4S ports or persist volume attached.

Expected: TLS negotiation succeeds and the output identifies the intended certificate and supported protocols/ciphers. For a connection or handshake failure, correlate the result with [listener ownership](#listener-ownership) and [collector logs](#container-status-and-logs). If the listener requires mutual TLS, this command supplies no client certificate; a client-certificate rejection alone does not prove a broken listener.

Return the target/time and relevant connection, handshake, certificate, or protocol findings. A successful TLS test does not prove syslog delivery or that the actual sender trusts the certificate.

## Packet arrival

Use an existing sample/capture first. If arrival is uncertain, observe a short sender/port-scoped interval on the collector interface:

```bash
sudo timeout 15s tcpdump -ni any -s 0 -c 20 -A 'src host 192.0.2.10 and udp dst port 514'
```

Replace source IP, interface, port, and protocol. If `timeout` is unavailable, stop manually after 15 seconds; packet count alone does not bound duration. Return whether packets arrived and, for a parsing problem, only a relevant sanitized raw message. Arrival does not prove parser/HEC delivery; TLS payloads are encrypted.

## Sample replay

When a replay is requested/authorized, inject one sanitized sample from a local file with the required newline/framing, using a known test host:

```bash
SC4S_HOST='sc4s.example.com'           # actual collector address
SC4S_PORT=514                        # actual listener port
SAMPLE_FILE='/tmp/sc4s-sample.log'     # existing one-event file
nc -w 2 "$SC4S_HOST" "$SC4S_PORT" < "$SAMPLE_FILE"
# For UDP instead:
nc -u -w 2 "$SC4S_HOST" "$SC4S_PORT" < "$SAMPLE_FILE"
```

Set the actual address, port, and path; choose one command. Confirm local `nc` option/EOF behavior and stop after the short test if it stays open. Plaintext `nc` does not test TLS; a local replay does not verify a remote sender's path. Compare the relevant collector log/counter before and after.

## Configuration and raw sample

For configuration errors, inspect only the implicated settings/rows below. For parsing or timestamp questions, use one complete raw message with PRI/header/timestamp only when needed; for metadata, use the expected versus reported values. Select the affected file at the actual host mount:

| Evidence | Standard host location |
| --- | --- |
| Relevant listener, HEC, TLS, proxy, buffer, or timezone assignment | `/opt/sc4s/env_file` |
| Affected custom parser, including embedded filters/rewrites | `/opt/sc4s/local/config/app_parsers/` |
| Affected standalone filter definition | `/opt/sc4s/local/config/filters/*.conf` |
| Affected custom routing/log path | `/opt/sc4s/local/config/log_paths/*.conf` |
| Active vendor/product metadata row | `/opt/sc4s/local/context/splunk_metadata.csv` |
| Relevant compliance filter and matching rows | `/opt/sc4s/local/context/compliance_meta_by_source.conf` and `.csv` |

Files ending in `.example` are not active overrides. Return only the relevant sanitized message/file excerpt; never source an env file or dump all environment variables. Prefer existing samples over debug/RAWMSG changes.

## Configuration validation

Use the first startup/preflight syntax error from [container logs](#container-status-and-logs) or [systemd logs](#systemd-status-and-logs), including filename/line. Validate pending edits in an isolated same-release environment through normal startup. Do not source env files or rerun the entrypoint inside a live collector. Syntax success alone does not prove matching or delivery.

## Resource usage

Select the command for the affected resource:

```bash
sudo "$RUNTIME" stats --no-stream "$CONTAINER"   # CPU/RAM
sudo "$RUNTIME" exec "$CONTAINER" df -h /var/lib/syslog-ng
sudo "$RUNTIME" exec "$CONTAINER" df -i /var/lib/syslog-ng
```

Use the actual persist path; if stopped, check its host mount. Return only the affected usage/filesystem. Inspect limits/mounts when the result requires them. Allocated buffer-file size does not measure queued messages.

## Archive and debug sizes

At the actual archive/debug mount, identify which directory accounts for disk growth:

```bash
sudo du -sh /opt/sc4s/archive/*         # substitute the actual directory
```

Return the growing directory and size. Check enabled destinations in the [configuration excerpt](#configuration-and-raw-sample); do not delete archives or buffers automatically.

## TCP backlog

Inspect established connections at the configured ports in the SC4S network namespace. Choose the affected direction:

```bash
sudo ss -tinomp state established '( sport = :514 or sport = :601 or sport = :6514 )'
sudo ss -tinomp state established '( dport = :8088 )'
```

Use `443` when appropriate for HEC. Return persistent inbound `Recv-Q` or outbound `Send-Q` growth across samples. A brief spike is insufficient; correlate with SC4S queue/error results.

## UDP receive errors

For suspected receive drops or an evidenced buffer warning, measure UDP errors and read kernel buffer limits:

```bash
netstat -su
sysctl net.core.rmem_default net.core.rmem_max
```

Compare receive-error counters during affected traffic and the limits against the SC4S log's requested buffer size. Return only those values and the warning. A `SO_RCVBUF` warning alone is not a failure.

## Kubernetes and BYOE

Adapt only the selected check. For Kubernetes, use the existing context and specify the collector container:

```bash
NAMESPACE=sc4s                       # actual namespace
POD=sc4s-example                     # actual collector pod
CONTAINER=sc4s                       # actual collector container
kubectl -n "$NAMESPACE" get pod "$POD"
kubectl -n "$NAMESPACE" logs "$POD" -c "$CONTAINER" --since=15m --timestamps --tail=100
```

Request previous logs with `--previous` only after a restart. For counters/version, replace the runtime exec prefix with `kubectl -n "$NAMESPACE" exec "$POD" -c "$CONTAINER" --`. Inspect only SC4S's state, limits, mounts, or Service when implicated; do not investigate unrelated pods/cluster services or dump Secrets.

For BYOE, use the actual SC4S service, config path, and syslog-ng control socket. Adapt journal/stats commands to that process; a container or management API is optional.

## Documentation

Select the deployed release's relevant section of [SC4S startup/validation](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_SC4S_server/) or [logging/resources](https://splunk.github.io/splunk-connect-for-syslog/main/troubleshooting/troubleshoot_resources/). Repository docs also contain statistics/TCP checks that published versions may lack.
