# SC4S MCP Server

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- A running SC4S instance (Docker or Podman) for management tools

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

## Container deployment

The MCP server image is OCI-compatible and works with both Docker and Podman. Replace `docker` with `podman` in the commands below if you use Podman.

### Build

```bash
docker build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
# or
podman build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
```

### Run with Docker

```bash
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

### Run with Podman

With Podman, locally-built images are stored under the `localhost/` prefix. If you build as a regular user but run via a system service (root), you must build with `sudo` because rootful and rootless Podman have separate image stores.

```bash
# Build as root so system services can find the image
sudo podman build -t sc4s-mcp -f sc4s_mcp/Dockerfile .

# Run, pointing to your SC4S instance
sudo podman run -d \
  -p 8000:8000 \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  localhost/sc4s-mcp
```

On a **Linux VM** where SC4S runs on the same host, use `--network host`:

```bash
sudo podman run -d --network host \
  -e SC4S_API_URL=http://127.0.0.1:8080 \
  --name sc4s-mcp \
  localhost/sc4s-mcp
```

### Cursor configuration (remote)

After starting the MCP container (Docker or Podman), add to `.cursor/mcp.json` on your local machine:

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

> **Not covered in the official SC4S documentation.** The standard deployment uses the `--env-file` flag, which is enough for normal operation but not for the MCP management tools.

The `--env-file` Docker/Podman flag reads the file from the host at startup and injects environment variables, but **does not make the file visible inside the container**. The MCP tools (`sc4s_set_env`, `sc4s_get_env`) need to read and write the file at runtime, so it must be bind-mounted as well:

```
-v /opt/sc4s/env_file:/opt/sc4s/env_file:z
```

Both the `--env-file` flag and the `-v` mount are needed — they serve different purposes.

#### systemd service

Add the mount variable to your SC4S unit file alongside the existing `Environment` lines:

```ini
Environment="SC4S_ENV_FILE_MOUNT=/opt/sc4s/env_file:/opt/sc4s/env_file:z"
```

Then add `-v "$SC4S_ENV_FILE_MOUNT"` to the `ExecStart` run command:

```ini
ExecStart=/usr/bin/podman run \
        -e "SC4S_CONTAINER_HOST=${SC4SHOST}" \
        -v "$SC4S_PERSIST_MOUNT" \
        -v "$SC4S_LOCAL_MOUNT" \
        -v "$SC4S_ARCHIVE_MOUNT" \
        -v "$SC4S_TLS_MOUNT" \
        -v "$SC4S_ENV_FILE_MOUNT" \
        --env-file=/opt/sc4s/env_file \
        --network host \
        --name SC4S \
        --rm $SC4S_IMAGE
```

Then reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart sc4s
```
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