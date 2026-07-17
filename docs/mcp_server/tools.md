# Tools

Tools are callable functions that the MCP client (and the AI assistant
behind it) can invoke. The SC4S MCP server groups tools into four
categories:

* **Repository / documentation**: read-only, safe to call at any time.
  These tools only read content that is baked into the MCP container
  image.
* **Configuration generation**: executes the copy of
  `configuration-tool.sh` baked into the MCP image. It generates text
  locally and does not contact or modify an SC4S instance.
* **SC4S instance management**: thin wrappers over the SC4S management
  REST API. These tools can change SC4S configuration and trigger a
  `syslog-ng` restart **inside the SC4S container**.
* **Splunk and compliance metadata**: specialized management tools for
  `splunk_metadata.csv` and `compliance_meta_by_source` overrides.

!!! important "How tools make changes"
    Management tools never execute shell commands. They send a single
    HTTP request to the SC4S management API at `SC4S_API_URL`. The API
    validates the input, stages the change, and restarts `syslog-ng`
    inside the SC4S container. If validation fails, the SC4S API rolls
    back the change automatically.

## Repository and documentation tools

These tools read static content from the MCP container. They make no
outbound calls and cannot modify anything.

| Tool | Description |
|---|---|
| `list_vendors()` | Lists all vendors supported by SC4S, based on the subdirectories of `docs/sources/vendor/`. |
| `list_all_parsers()` | Lists all `.conf` parser files from `package/lite/etc/addons/`. |
| `list_vendor_parsers(vendor)` | Lists parser files whose contents reference a vendor name (case-insensitive whole-word match). |
| `get_parser(parser_name)` | Returns the content of a parser file. Accepts either the file name (`foo.conf`) or the stem (`foo`). Returns `{ "found": bool, "path": ..., "content": ... }`. |
| `search_docs(query)` | Regex search across every markdown file under `docs/`. Returns `path:line: snippet` entries. |
| `get_parser_creation_guide()` | Returns the full parser-creation guide (`SKILL.md` + testing reference). The assistant calls this automatically when a user asks to create a parser. |

## Configuration generation

`sc4s_build_config(...)` executes the actual `configuration-tool.sh` shipped
in the MCP image in non-interactive mode and returns `{config, warnings}`. It
accepts Splunk HEC settings plus custom or hardware-profile tuning options.
The script remains the source of truth for defaults, hardware thresholds, and
the emitted `env_file`; the MCP tool does not reconstruct that configuration
in Python.

This tool only generates content and does not modify SC4S. To apply its
result, read the current file with `get_env`, choose merge or replace, preview
the complete final file, confirm the exact payload, call `set_env`, and poll
`get_job_status` until the job reaches `success` or `failed`.

## SC4S instance management tools

These tools require a reachable SC4S instance at `SC4S_API_URL`. If the
instance is unreachable, you will see an error payload
`{"status": "error", "message": "SC4S instance unreachable at ..."}`
instead of a failure inside your SC4S container.

### Health and general configuration

| Tool | Description |
|---|---|
| `sc4s_health()` | Returns the health payload from the SC4S management API. Use this first when troubleshooting. |
| `get_job_status(job_id)` | Polls a configuration job until its status is `success` or `failed`. |
| `get_env()` | Reads the current `env_file` from the running SC4S instance. |
| `set_env(env_file_content)` | Uploads a new `env_file` and returns an asynchronous job ID. |

### Custom parsers

| Tool | Description |
|---|---|
| `list_custom_parsers()` | Lists all custom parsers currently deployed on the SC4S instance. |
| `get_custom_parser(name)` | Reads the content of a deployed custom parser. |
| `add_parser(filename, content)` | Uploads a new `.conf` parser and returns an asynchronous job ID. |
| `delete_parser(name)` | Deletes a custom parser and returns an asynchronous job ID. |

### Splunk metadata (`splunk_metadata.csv`)

These tools manage per-vendor/product overrides that SC4S sends to Splunk
(index, source, sourcetype, host, template).

| Tool | Description                                                                                                                                                                                            |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `get_splunk_metadata()` | Reads `splunk_metadata.csv` entries. Each entry is `{ key, metadata, value }`, where `metadata` is one of `index, source, sourcetype, host, sc4s_template` and `key` is a `vendor_product` identifier. |
| `set_splunk_metadata(entries)` | Overwrites `splunk_metadata.csv` and returns an asynchronous job ID. Example entry: `{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}`. |
| `delete_splunk_metadata()` | Clears all Splunk metadata overrides and returns an asynchronous job ID. |

### Compliance metadata (`compliance_meta_by_source`)

These tools manage the filter definitions and CSV rows used to redirect
events to different Splunk indexes (or add indexed fields) based on
host, IP, or subnet matching.

| Tool | Description |
|---|---|
| `get_compliance_overrides()` | Reads both the `.conf` filter definitions (`conf_content`) and the CSV rows (`csv_content`). |
| `set_compliance_override(conf_content, csv_content)` | Overwrites both files and returns an asynchronous job ID. `field_name` must be `.splunk.index`, `.splunk.source`, `.splunk.sourcetype`, or `fields.<name>`. |
| `delete_compliance_override()` | Clears both files and returns an asynchronous job ID. |

Any tool that modifies the SC4S configuration returns the ID of the job
performing the update. Call `get_job_status(job_id)` to check whether the job
is `in_progress`, `success`, or `failed`.

If you try to start another job while one is already running, the API returns
HTTP `409 Conflict` with details about the active job. Wait for that job to
finish before retrying.

Example `conf_content`:

```
filter f_pci_zone { host("pci-*" type(glob)) or netmask(10.1.0.0/16) };
```

Example `csv_content` entry:

```json
{
  "filter_name": "f_pci_zone",
  "field_name": ".splunk.index",
  "value": "pci_idx"
}
```

## Error handling

All management tools return structured JSON. When something goes wrong,
you will get a payload with a `status: "error"` field, and one of:

| Field | Meaning |
|---|---|
| `message` | Human-readable error (connection refused, timeout, transport-level failure). |
| `http_status` + additional fields | The SC4S management API returned a non-2xx HTTP response. The extra fields come from the API's JSON body (typically `detail` or `error`). |
