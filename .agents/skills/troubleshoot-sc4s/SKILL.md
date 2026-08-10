---
name: troubleshoot-sc4s
description: Diagnose a running SC4S instance through its MCP server. Use when SC4S is unhealthy or unreachable, events are missing or misrouted, parser behavior is unexpected, Splunk metadata looks wrong, or a configuration job failed.
---

# Troubleshoot SC4S

Build an evidence-backed diagnosis from live, read-only SC4S state. Do not mutate the instance merely because a likely fix is apparent.

## Discover the SC4S tools

Find a callable tool whose name ends with `sc4s_health`. Store everything before that suffix as `{SC4S_NS}` and use the same namespace prefix for every SC4S tool below.

If no matching tool is callable, explain that live diagnosis requires an SC4S MCP connection. Ask for the relevant health response, runtime logs, `env_file`, and custom parser content so diagnosis can continue manually. Warn the user to redact HEC tokens and other secrets.

## Establish the symptom

Ask only for details that are still missing:

- What is failing: management access, SC4S health, ingestion, routing, parsing, or a configuration job?
- When did it start, and what changed immediately beforehand?
- Is every source affected or only a vendor, product, host, protocol, or destination?
- What was expected, and what was actually observed in Splunk or SC4S?

Do not require the user to answer every question before running safe baseline checks.

## Collect a read-only baseline

1. Call `{SC4S_NS}sc4s_health`.
2. Call `{SC4S_NS}get_env` to test whether the live management routes are available.
   - If it returns env content, use relevant assignments in the diagnosis, but redact HEC tokens and credentials from all output.
   - If it returns the JSON error `env_file not found`, report that the management route is enabled but the file itself is missing. Do not propose a replacement without a known baseline.
   - If `sc4s_health` succeeds but `get_env` returns a route-level 404 or the management endpoint is unavailable, infer that the management API may be disabled or not exposed. Do not call other live configuration, parser, metadata, or job tools. Ask the operator to verify `SC4S_API_MANAGEMENT_ENABLED=true` in the host's `env_file` and restart SC4S externally.
3. Only when the management routes are available, call `{SC4S_NS}list_custom_parsers`.
4. If the symptom names a custom parser and the management routes are available, call `{SC4S_NS}get_custom_parser` for it.
5. If the symptom concerns an existing vendor parser, call `{SC4S_NS}list_vendor_parsers`, then `{SC4S_NS}get_parser` for the closest match. These repository-backed tools remain useful when live management routes are unavailable.
6. Call `{SC4S_NS}search_docs` with a narrow query derived from the symptom, vendor, product, or setting. Prefer SC4S documentation over general syslog-ng assumptions.

When a prior mutation returned a job ID, call `{SC4S_NS}get_job_status(job_id)`. Poll while its status is `in_progress`; interpret only `success` and `failed` as terminal.

If one read fails, report that evidence gap and continue with the remaining safe checks when possible. Do not infer that SC4S is healthy from MCP server reachability alone.

## Diagnose systematically

Separate facts from conclusions:

1. **Observed evidence** — summarize tool results and user observations without exposing secrets.
2. **Most likely cause** — connect the evidence to one cause and state confidence.
3. **Alternatives** — list only plausible competing causes and the evidence that would distinguish them.
4. **Next check** — recommend the smallest read-only check that reduces uncertainty.
5. **Proposed fix** — describe the minimal change, its effect, restart impact, and rollback path.

Use these diagnostic branches:

- Management API unavailable: when health is reachable but live management routes are not, explain that `SC4S_API_MANAGEMENT_ENABLED` may be unset or false. The unavailable API cannot confirm its own host setting. Ask the operator to verify `SC4S_API_MANAGEMENT_ENABLED=true` in the host's `env_file` and restart SC4S externally; do not suggest further live configuration calls until the routes are reachable.
- SC4S unhealthy after a change: inspect the terminal job result, affected configuration or parser content, and likely syntax or restart errors. Do not claim rollback occurred unless the job result says so.
- Events missing for one source: compare the source identity to built-in and custom parser filters; check protocol and source-specific configuration; then check the expected `vendor_product` and Splunk metadata.
- Events present but misrouted: inspect parser metadata defaults and the current Splunk metadata overrides before suggesting parser changes.
- All sources missing: prioritize runtime health, HEC destination settings, TLS verification, token presence, and transport configuration over a single parser.

## Apply a fix only when requested

Diagnosis is read-only by default. If the user explicitly asks to apply the proposed fix:

If the management routes were unavailable during baseline checks, stop this workflow. Explain that live mutation cannot proceed until the operator enables the management API and restarts SC4S externally.

1. Re-read the affected live state immediately before planning the mutation.
2. Show the exact final payload or parser diff. Preserve unrelated state.
3. Warn that `set_env`, `set_splunk_metadata`, and `set_compliance_override` replace their complete files. Warn that `add_parser` replaces all content of an existing filename.
4. Explain that SC4S will restart, then obtain fresh explicit confirmation immediately before the mutation. Earlier approval of the diagnosis is not mutation confirmation.
5. Call the chosen mutation tool once. Treat a missing or malformed `job_id` as an unsuccessful submission.
6. Poll `{SC4S_NS}get_job_status(job_id)` while `in_progress`. Report success only for terminal `success`; on `failed`, report the error without automatic retry or rollback.
7. On success, re-read the affected state and call `{SC4S_NS}sc4s_health`. Distinguish an applied job from a fully verified healthy result.