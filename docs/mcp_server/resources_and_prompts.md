# Resources and prompts

In addition to [tools](tools.md), the SC4S MCP server exposes two other
MCP primitives:

* **Resources** — read-only documents that the assistant (or the user)
  can request by URI. Resources are static content baked into the MCP
  container image; they do not touch SC4S or the host.
* **Prompts** — pre-built workflows that seed a conversation with all
  the context needed for a specific task. Prompts do not execute code
  on their own — they just structure the conversation.

## Resources

All resources use the `sc4s://` URI scheme. They are assembled from the
project's markdown documentation at the time they are fetched, so they
always match the docs that ship with the image you are running.

| URI | Contents |
|---|---|
| `sc4s://docs/creating_parsers` | The full parser-creation guide: the `index.md`, `filter_message.md`, `parse_message.md`, and `unit_tests.md` chapters, concatenated. Use this to give the assistant the conventions it needs to write a correct parser. |
| `sc4s://docs/troubleshooting` | The troubleshooting guide: startup/validation checks, logging resources, PCAP replay, and Splunk health checks, concatenated. Use this when diagnosing a problem. |
| `sc4s://docs/vendor/{vendor}` | All markdown documentation for a given vendor under `docs/sources/vendor/{vendor}/`. Replace `{vendor}` with a directory name — the list is available from the `list_vendors` tool. |

### Example usage

In Cursor (or any client that supports attaching resources to a chat),
you can include a resource so the assistant sees the full guide:

* Attach `sc4s://docs/creating_parsers` when you ask *"help me write a
  parser for vendor X"*.
* Attach `sc4s://docs/troubleshooting` when you ask *"events are not
  showing up in Splunk"*.
* Attach `sc4s://docs/vendor/cisco` when you ask *"what does SC4S already
  support for Cisco?"*.

Resources are read-only by construction — they return text, nothing
else. The server cannot use them to modify state.

## Prompts

Prompts are ready-made workflows that include the relevant knowledge
base and a set of diagnostic steps. Invoke them from your client's
prompt picker (Cursor: `⌘/` then *Prompts*, or the MCP panel; other
clients expose a similar menu).

### `create_parser`

Guided workflow for authoring a new SC4S syslog-ng parser from sample
logs. The prompt loads the project's parser-creation knowledge base and
asks the assistant to follow those conventions exactly.

**Parameters**

| Name | Description |
|---|---|
| `vendor` | Vendor name (free text, for example `cisco`). |
| `product` | Product name (free text, for example `asa`). |
| `sample_logs` | One or more raw log lines to base the parser on. |

**Typical flow after invocation**

1. The assistant reads the knowledge base and the sample logs.
2. It calls `list_vendor_parsers` / `get_parser` to learn existing
   conventions for the same vendor (if any).
3. It drafts a new `.conf` parser and the corresponding unit tests.
4. With your approval, it uploads the parser via `sc4s_add_parser`.

### `troubleshoot_sc4s`

Guided workflow for diagnosing a live SC4S issue. The prompt loads the
troubleshooting docs and asks the assistant to run the standard
diagnostic sequence before making any changes.

**Parameters**

| Name | Description |
|---|---|
| `symptom` | Free-text description of what you are seeing (for example, *"no Cisco ASA events in Splunk since 10:30"*). |

**Diagnostic steps seeded by the prompt**

1. Call `sc4s_health` to check the instance status.
2. Call `sc4s_get_env` to review the current configuration.
3. Call `sc4s_list_custom_parsers` to list deployed custom parsers.
4. Propose specific fixes.
5. Apply configuration changes via `sc4s_set_env` only after explaining
   the reasoning.

## Combining tools, resources, and prompts

A typical interaction uses all three primitives together. For example,
adding support for a new vendor might look like this:

1. Invoke the `create_parser` prompt with vendor, product, and sample
   logs.
2. The assistant pulls context from `sc4s://docs/creating_parsers` and
   calls read-only tools (`list_vendors`, `list_vendor_parsers`,
   `get_parser`) to inspect existing work.
3. After you review the draft, the assistant calls `sc4s_add_parser`
   to deploy it.
4. If the SC4S management API rejects the parser, the change is rolled
   back automatically and the assistant iterates.

Throughout this flow the MCP server itself only reads files from its own
container and makes HTTP calls to `SC4S_API_URL`. See
[Security model](index.md#security-model-no-host-command-execution) for
details.
