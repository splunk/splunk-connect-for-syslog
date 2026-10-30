# SC4S MCP workflow

Discover callable SC4S tools and their schemas; use their actual namespace, not a guessed prefix. Skip unavailable capabilities and use [operator commands](operator-commands.md#runtime-and-paths). Repository-backed tools do not prove live collector state.

## Select reads by symptom

- `sc4s_health`: process/queue health when relevant. A healthy result may omit queue checks and does not prove delivery.
- `get_env`: only for a suspected SC4S configuration problem. Inspect affected assignments, avoid exposing returned secrets, and do not request an operator env dump as well.
- `list_custom_parsers` / `get_custom_parser`: only the affected parsing/filter path.
- `get_splunk_metadata` / `get_compliance_overrides`: only routing/metadata symptoms. These inspect SC4S override files, not Splunk.
- `list_vendor_parsers` / `get_parser`: affected built-in vendor behavior; these read the MCP repository, which may differ from the deployed release.
- `search_docs`: narrow symptom/vendor/setting regex; read the matching surrounding docs.
- `get_job_status(job_id)`: only for an existing submitted change.

Use [operator logs](operator-commands.md#container-status-and-logs), [counters](operator-commands.md#counter-trends), or an [affected raw sample/configuration excerpt](operator-commands.md#configuration-and-raw-sample) only when missing from the evidence. Do not invent tools for logs/statistics.

## API access errors

- Route HTTP 404: management may be disabled or unsupported. A JSON `env_file not found` instead means the route exists but its backing file is missing. Continue with host evidence.
- HTTP 401: check the configured MCP `SC4S_API_TOKEN` / `SC4S_API_TOKEN_FILE` against collector `SC4S_AUTH_TOKEN_FILE` locally, without exposing values.
- Connect/TLS/timeout: inspect MCP `SC4S_API_URL` and `SC4S_API_CA_CERT` only if MCP access is the reported issue; otherwise continue diagnosis manually.

Do not enable management, disable authentication, or bypass TLS to troubleshoot ingestion. For release-specific API details, consult `docs/configuration.md` and `docs/mcp_server/installation.md` from that release.

## Apply an authorized SC4S change

1. Confirm the chosen write and job-status tools are available. Re-read the affected live state and prepare the exact change, preserving unrelated content and a rollback baseline; explain restart impact.
2. `set_env`, `set_splunk_metadata`, and `set_compliance_override` replace complete files; the last replaces both `.conf` and `.csv`. `add_parser` overwrites an existing filename. Include retained content in replacement payloads.
3. Submit once. An accepted response/job ID means submitted, not applied. A missing ID or timeout leaves submission uncertain: inspect state/status before retrying.
4. Poll `get_job_status` at bounded intervals while `in_progress`; `success` / `failed` are terminal. If progress persists or status is unavailable, report pending/unknown and hand off. On failure, capture the error and relevant logs; do not automatically resubmit or claim rollback.
5. On success, re-read affected state and relevant health/log/counter evidence. Request user event confirmation only when needed; job success alone is not recovery.

For HTTP 409, wait for the identified active job, then re-read state and rebuild the payload. Never retry a stale replacement. Old job records can disappear after restart; a missing record proves neither success nor failure. Older releases may lack asynchronous jobs: follow that release's contract.
