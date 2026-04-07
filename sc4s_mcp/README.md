# SC4S MCP Server

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- A running SC4S instance (Docker) for management tools

## Installation

```bash
cd sc4s_mcp
poetry install
```

## Running the MCP server

### Local mode (stdio — for Cursor on the same machine)

```bash
poetry run python sc4s_mcp/server.py
```

### Remote mode (SSE — for Cursor on a different machine)

```bash
poetry run python sc4s_mcp/server.py --sse
```

The server listens on `0.0.0.0:8000` by default. Customize with environment variables:

| Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Transport mode (`stdio` or `sse`). Overrides `--sse` flag. |
| `MCP_HOST` | `0.0.0.0` | Bind address for SSE mode |
| `MCP_PORT` | `8000` | Port for SSE mode |
| `SC4S_API_URL` | `http://localhost:8080` | URL of the SC4S healthcheck API inside the container |

## Cursor configuration

### Local (stdio)

Add to `.cursor/mcp.json` in the repo root:

```json
{
  "mcpServers": {
    "sc4s": {
      "command": "bash",
      "args": ["-c", "cd \"$PWD\" && poetry run python sc4s_mcp/server.py"]
    }
  }
}
```

### Remote (SSE)

Add to `.cursor/mcp.json` on your local machine:

```json
{
  "mcpServers": {
    "sc4s": {
      "url": "http://<VM_IP>:8000/sse"
    }
  }
}
```

## Docker deployment

```bash
# Build from the repo root
docker build -t sc4s-mcp -f sc4s_mcp/Dockerfile .

# Run, pointing to your SC4S instance
docker run -d \
  -p 8000:8000 \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  sc4s-mcp
```

On a **Linux VM** where SC4S runs on the same host, use `--network host` so the MCP container can reach SC4S via `localhost`:

```bash
docker run -d --network host \
  -e SC4S_API_URL=http://127.0.0.1:8080 \
  --name sc4s-mcp \
  sc4s-mcp
```

Then add to `.cursor/mcp.json` on your local machine:

```json
{
  "mcpServers": {
    "sc4s": {
      "url": "http://<VM_IP>:8000/sse"
    }
  }
}
```

## SC4S container setup

The MCP management tools (`sc4s_set_env`, `sc4s_add_parser`, etc.) communicate with the Flask API running inside the SC4S container on the healthcheck port (default 8080).

### Required: mount the env_file

By default SC4S uses `--env-file` to inject environment variables at container startup, but the file itself is **not** accessible inside the container. For the `sc4s_set_env` tool to work, the env_file must be bind-mounted into the container:

```
-v /opt/sc4s/env_file:/opt/sc4s/env_file:z
```

Add this to your `systemd` service file or `docker run` command. For example, in the service file add an environment variable:

```ini
Environment="SC4S_ENV_FILE_MOUNT=/opt/sc4s/env_file:/opt/sc4s/env_file:z"
```

And reference it in the `ExecStart` `docker run` command:

```
-v "$SC4S_ENV_FILE_MOUNT"
```

> **Note:** The parsers directory does **not** need an extra mount. The standard SC4S local mount (`/opt/sc4s/local` → `/etc/syslog-ng/conf.d/local`) already covers the custom parsers path. Just make sure the subdirectory exists on the host:
>
> ```bash
> sudo mkdir -p /opt/sc4s/local/config/app_parsers
> ```

## Available tools

### Read-only (repo / docs)

| Tool | Description |
|---|---|
| `list_vendors` | List all vendors supported by SC4S |
| `list_all_parsers` | List all `.conf` parser files from the addons directory |
| `list_vendor_parsers(vendor)` | List parsers matching a vendor name |
| `get_parser(parser_name)` | Return the content of a specific parser file |
| `search_docs(query)` | Regex search across all documentation markdown files |
| `get_parser_creation_guide` | Full parser creation guide with syntax, filter topics, rewrite functions, examples, and checklist. Called automatically when a user asks to create a parser. |

### SC4S instance management (requires running SC4S)

| Tool | Description |
|---|---|
| `sc4s_health` | Check the health of the running SC4S instance |
| `sc4s_get_env` | Read the current `env_file` from the running instance |
| `sc4s_set_env(env_file_content)` | Upload a new `env_file`, backup the old one, and restart syslog-ng |
| `sc4s_add_parser(filename, content)` | Upload a `.conf` parser, validate syntax, and restart syslog-ng |
| `sc4s_delete_parser(name)` | Delete a custom parser, validate config, and restart syslog-ng |
| `sc4s_list_custom_parsers` | List all custom parsers deployed on the instance |
| `sc4s_get_custom_parser(name)` | Read the content of a deployed custom parser |

### Resources

| Resource | Description |
|---|---|
| `sc4s://docs/creating_parsers` | Full parser creation guide |