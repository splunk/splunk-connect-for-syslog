---
name: manage-splunk-metadata
description: Inspect and safely add, update, remove, or clear SC4S Splunk metadata overrides through MCP. Use for vendor_product index, source, sourcetype, host, or sc4s_template overrides in splunk_metadata.csv.
---

# Manage Splunk Metadata

Manage the live `splunk_metadata.csv` as a full-replacement resource while preserving entries the user did not ask to change.

## Discover the SC4S tools

Find a callable tool whose name ends with `get_splunk_metadata`. Store everything before that suffix as `{SC4S_NS}`. Use the same prefix for `set_splunk_metadata`, `delete_splunk_metadata`, `get_job_status`, and `sc4s_health`.

If no matching read tool is callable, explain that this workflow requires an SC4S MCP connection and stop before proposing a live mutation.

## Read and interpret current state

Always call `{SC4S_NS}get_splunk_metadata` before planning a change. Treat each entry as:

```json
{"key": "vendor_product", "metadata": "index", "value": "target_value"}
```

Allow only these metadata fields: `index`, `source`, `sourcetype`, `host`, and `sc4s_template`.

Use `(key, metadata)` as the logical identity when matching an entry. Preserve unrelated entries and their order. Append new entries after existing entries unless the user requests another order. If the current file contains duplicate logical identities, show them and ask how to resolve them; do not silently collapse or reorder them.

For read-only requests, present a compact table and do not ask for mutation confirmation.

## Build a proposed change

Determine whether the user wants to add, update, remove, or clear entries:

- Add: require non-empty `key`, allowed `metadata`, and `value`; reject an ambiguous duplicate identity.
- Update: match exactly one current `(key, metadata)` and change only its value.
- Remove: match the exact identity and remove only that entry.
- Clear: remove every entry by using `delete_splunk_metadata`.

Before any write:

1. Re-read current metadata so the proposal is based on the latest live state.
2. Build the complete final `entries` list, not only the changed rows.
3. Validate every entry has exactly the required semantic fields and an allowed metadata name.
4. Show an added/changed/removed summary and the complete replacement payload.
5. State prominently that `set_splunk_metadata` overwrites the entire live file and that unrelated rows are preserved only because they are included in the payload. For clear, state that every override will be removed.
6. Explain that applying the change restarts SC4S and obtain fresh explicit confirmation immediately before the tool call. An earlier discussion or approval is not confirmation to mutate.

## Apply and verify

After explicit confirmation:

1. For add, update, or partial removal, call `{SC4S_NS}set_splunk_metadata(entries=<complete final list>)` exactly once.
2. For clear, call `{SC4S_NS}delete_splunk_metadata` exactly once.
3. Require a non-empty, well-formed `job_id`; otherwise report an unsuccessful submission and stop.
4. Call `{SC4S_NS}get_job_status(job_id)` and keep polling while status is `in_progress`.
5. On terminal `failed`, report the error and stop. Do not claim the file changed, retry, or roll back automatically.
6. Only on terminal `success`, call `{SC4S_NS}get_splunk_metadata` again and compare the returned entries with the intended final state. Then call `{SC4S_NS}sc4s_health`.
7. Report full success only if the job succeeded, read-back matches, and SC4S is healthy. Otherwise distinguish job completion from verification failure.