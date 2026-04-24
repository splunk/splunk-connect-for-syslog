# Tools

Tools are callable functions that the MCP client (and the AI assistant
behind it) can invoke. The SC4S MCP server groups tools into three
categories:

* **Repository / documentation**: read-only, safe to call at any time.
  These tools only read content that is baked into the MCP container
  image.
* **SC4S instance management**: thin wrappers over the SC4S management
  REST API. These tools can change SC4S configuration and trigger a
  `syslog-ng` restart **inside the SC4S container**.
* **Splunk & compliance metadata**: specialized management tools for
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

## SC4S instance management tools

These tools require a reachable SC4S instance at `SC4S_API_URL`. If the
instance is unreachable, you will see an error payload
`{"status": "error", "message": "SC4S instance unreachable at ..."}`
instead of a failure inside your SC4S container.

### Health and general configuration

| Tool | Description |
|---|---|
| `sc4s_health()` | Returns the health payload from the SC4S management API. Use this first when troubleshooting. |
| `sc4s_get_env()` | Reads the current `env_file` from the running SC4S instance. |
| `sc4s_set_env(env_file_content)` | Uploads a new `env_file`. The SC4S API backs up the previous file, applies the new one, and restarts `syslog-ng`. On validation failure the previous file is restored. |

### Custom parsers

| Tool | Description |
|---|---|
| `sc4s_list_custom_parsers()` | Lists all custom parsers currently deployed on the SC4S instance. |
| `sc4s_get_custom_parser(name)` | Reads the content of a deployed custom parser. |
| `sc4s_add_parser(filename, content)` | Uploads a new `.conf` parser. The `.conf` extension is added if missing. SC4S validates syntax and restarts `syslog-ng`; invalid parsers are rolled back. |
| `sc4s_delete_parser(name)` | Deletes a custom parser. SC4S re-validates the remaining configuration and restarts `syslog-ng`; if validation fails, the parser is restored. |

### Splunk metadata (`splunk_metadata.csv`)

These tools manage per-vendor/product overrides that SC4S sends to Splunk
(index, source, sourcetype, host, template).

| Tool | Description |
|---|---|
| `sc4s_get_splunk_metadata()` | Reads `splunk_metadata.csv` entries. Each entry is `{ key, metadata, value }`, where `metadata ∈ { index, source, sourcetype, host, sc4s_template }` and `key` is a `vendor_product` identifier. |
| `sc4s_set_splunk_metadata(entries)` | Overwrites `splunk_metadata.csv` with the provided list. SC4S restarts after applying. Example entry: `{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}`. |
| `sc4s_delete_splunk_metadata()` | Clears all Splunk metadata overrides. SC4S restarts after clearing. |

### Compliance metadata (`compliance_meta_by_source`)

These tools manage the filter definitions and CSV rows used to redirect
events to different Splunk indexes (or add indexed fields) based on
host, IP, or subnet matching.

| Tool | Description |
|---|---|
| `sc4s_get_compliance_overrides()` | Reads both the `.conf` filter definitions (`conf_content`) and the CSV rows (`csv_content`). |
| `sc4s_set_compliance_override(conf_content, csv_content)` | Overwrites both files. `csv_content` is a list of `{filter_name, field_name, value}` dicts, where `field_name` must be `.splunk.index`, `.splunk.source`, `.splunk.sourcetype`, or `fields.<name>`. SC4S restarts after applying. |
| `sc4s_delete_compliance_override()` | Clears both files, removing all compliance overrides. SC4S restarts after clearing. |

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