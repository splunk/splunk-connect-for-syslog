# SC4S MCP Server

The **SC4S MCP Server** is a [Model Context Protocol](https://modelcontextprotocol.io) server
that exposes Splunk Connect for Syslog (SC4S) knowledge and a safe management
API to any MCP-compatible client (Cursor, Claude Desktop, Visual Studio Code,
and others). It lets an AI assistant help you discover supported vendors,
author and validate syslog-ng parsers, inspect a running SC4S instance, and
apply configuration changes — all through well-defined MCP tools, resources,
and prompts.

## What it is

The server is shipped as a small containerized Python application based on
[FastMCP](https://github.com/jlowin/fastmcp). It provides three categories of
capabilities:

| Category | Purpose |
|---|---|
| **Tools** | Callable functions the assistant can invoke (for example, list vendors, get a parser, check SC4S health, upload a new parser). |
| **Resources** | Read-only documents the assistant can load on demand (parser creation guide, troubleshooting guide, vendor docs). |
| **Prompts** | Guided workflows (for example, `create_parser`, `troubleshoot_sc4s`) that orient the assistant to a specific task. |

The full list of tools, resources, and prompts is documented in
[Tools](tools.md) and [Resources and prompts](resources_and_prompts.md).

## How it fits into your environment

The MCP server runs in its own OCI container (Docker or Podman) and
communicates with:

1. Your **MCP client** (the IDE / assistant) — over `stdio` on the local
   machine, or over `SSE` (HTTP) when the client is remote.
2. The **SC4S container's management API** — an HTTP endpoint that lives on
   the SC4S healthcheck port (default `8080`) and handles configuration reads
   and writes for `env_file`, custom parsers, and Splunk metadata.

```
+-----------------+        stdio / SSE        +------------------+
|   MCP client    |  <-------------------->   |  SC4S MCP server |
| (Cursor, etc.)  |                           |    (container)   |
+-----------------+                           +---------+--------+
                                                        |
                                                HTTP    |
                                                        v
                                              +------------------+
                                              |  SC4S container  |
                                              |   (syslog-ng +   |
                                              |   Flask API)     |
                                              +------------------+
```

## Security model: no host command execution

!!! important "The MCP server never runs commands outside its container"
    The SC4S MCP server does **not** execute shell commands, scripts, or
    binaries on your host. It does **not** invoke `docker`, `podman`,
    `systemctl`, `syslog-ng`, `bash`, or any other process outside the
    container in which it runs.

    All management actions are performed by calling a well-defined HTTP API
    exposed by the SC4S container itself. That API — and only that API —
    decides what configuration is accepted, validates syntax, and restarts
    `syslog-ng` inside the SC4S container when needed.

Concretely, the MCP server only does two kinds of I/O:

* **Reads** a small, read-only set of files that are **baked into its own
  container image** at build time: the documentation under `docs/`, the
  parser library under `package/lite/etc/addons/`, and the parser-creator
  knowledge base. These are static; the MCP server does not reach into your
  host filesystem.
* **Makes HTTP(S) requests** to `SC4S_API_URL` (the Flask management API
  running inside the SC4S container). Every "management" tool is a thin
  wrapper over a single HTTP call; there is no shell, no `exec`, and no
  process spawning.

Additional hardening in the shipped image:

* Runs as a non-root user (`uid 10001`).
* No access to the Docker/Podman socket.
* No mounts of the host filesystem are required or recommended.
* Destructive operations (upload parser, change `env_file`, clear compliance
  metadata) are handled by the SC4S API, which validates and rolls back
  changes if `syslog-ng` fails to restart.

## What it does not do

* It does **not** run arbitrary commands on your host or inside the SC4S
  container.
* It does **not** send events to Splunk; event ingestion is the SC4S
  container's job.
* It does **not** modify files on the host filesystem.
* It does **not** open any outbound connection other than to the configured
  `SC4S_API_URL`.
* It does **not** require privileged mode, capabilities beyond the defaults,
  or access to `/var/run/docker.sock`.

## Next steps

* **[Installation](installation.md)** — build the image, run it with Docker
  or Podman, and configure your MCP client.
* **[Tools](tools.md)** — reference of every callable tool.
* **[Resources and prompts](resources_and_prompts.md)** — reference of the
  available MCP resources and guided prompts.
