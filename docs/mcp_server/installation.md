# Installing the SC4S MCP Server

The SC4S MCP server is distributed as a container image. It can be run on
your local workstation for use with a local AI assistant (using the
`stdio` transport), or on a shared host, such as the same machine as your
SC4S instance, where remote assistants and agents connect to it over the
`SSE` transport.

!!! note "No host commands are executed"
    Regardless of how you run the container, the MCP server itself never
    runs commands outside the container. See
    [Security model](index.md#security-model-no-host-command-execution).

## Prerequisites

* A running SC4S instance exposing the management REST API (default port
  `8080`).
* Docker or Podman on the host where the MCP server will run.
* An MCP-compatible AI assistant or agent that can connect to the server
  over `stdio` or `SSE` (for example, Cursor, Claude Desktop, or Visual
  Studio Code with an MCP extension).

## Configuration reference

The MCP server is configured through environment variables.

| Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` for local clients, `sse` for remote clients. |
| `MCP_HOST` | `0.0.0.0` | Bind address used in `sse` mode. |
| `MCP_PORT` | `8000` | TCP port used in `sse` mode. |
| `SC4S_API_URL` | `http://localhost:8080` | URL of the SC4S management REST API. The MCP server calls this URL for all management tools. |

## Build the image

The Dockerfile is part of the SC4S repository. Build from the repository
root so that the `docs/`, `package/lite/etc/addons/`, and
`.agents/skills/parser-creator/` directories are available to the build
context.

=== "Docker"

    ```bash
    docker build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
    ```

=== "Podman"

    ```bash
    podman build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
    ```

## Run the container

The examples below assume the SC4S container is reachable at
`http://<SC4S_HOST>:8080`. If SC4S runs on the same host, use
`--network host` and point `SC4S_API_URL` to `http://127.0.0.1:8080`.

=== "Docker"

    ```bash
    docker run -d \
      -p 8000:8000 \
      -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
      --name sc4s-mcp \
      sc4s-mcp
    ```

    Same host as SC4S (Linux):

    ```bash
    docker run -d --network host \
      -e SC4S_API_URL=http://127.0.0.1:8080 \
      --name sc4s-mcp \
      sc4s-mcp
    ```

=== "Podman"

    Locally built images are stored under the `localhost/` prefix.

    ```bash
    podman run -d \
      -p 8000:8000 \
      -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
      --name sc4s-mcp \
      localhost/sc4s-mcp
    ```

    Same host as SC4S (Linux):

    ```bash
    podman run -d --network host \
      -e SC4S_API_URL=http://127.0.0.1:8080 \
      --name sc4s-mcp \
      localhost/sc4s-mcp
    ```

The image ships a healthcheck that verifies the SSE endpoint is up. Check
the container status with:

```bash
docker ps   # or: podman ps
```

## Prepare your SC4S instance

The MCP management tools (`sc4s_set_env`, `sc4s_add_parser`, and others)
need to read and write SC4S's `env_file` at runtime. The `--env-file`
Docker/Podman flag alone is **not sufficient**: it injects variables at
startup but does not make the file visible inside the container.

Bind-mount the file in addition to passing `--env-file`:

```
-v /opt/sc4s/env_file:/opt/sc4s/env_file:z
```

### systemd unit example

If you run SC4S via systemd, add the mount variable:

```ini
Environment="SC4S_ENV_FILE_MOUNT=/opt/sc4s/env_file:/opt/sc4s/env_file:z"
```

and include `-v "$SC4S_ENV_FILE_MOUNT"` in your `ExecStart` alongside the
other `-v` flags:

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

### Generic MCP client configuration

Most MCP clients accept one of two connection styles. Consult your
client's documentation for the exact configuration file and its location;
the shape of the configuration is typically the same across clients.

**Local process (stdio)**: the client launches the server as a child
process and communicates via standard input/output. Provide:

* a `command` to execute (for example `docker` or `podman`),
* an `args` array that starts the MCP server,
* optional environment variables (`SC4S_API_URL`, `MCP_TRANSPORT=stdio`).

**Remote endpoint (SSE)**: the client connects to an HTTP URL exposing
the MCP SSE endpoint. Provide:

* a `url` pointing at `http://<MCP_HOST>:8000/sse`,
* any additional headers required by your deployment (for example, a
  reverse-proxy auth header).

## Verify the installation

1. Confirm the container is running: `docker ps` or `podman ps`.
2. Confirm the MCP client sees the server. Most clients list available
   MCP servers in a dedicated panel or on startup.
3. From the assistant, call the `sc4s_health` tool. A healthy instance
   returns a status payload from the SC4S management API. An error like
   *"SC4S instance unreachable at http://..."* means the MCP server
   could reach out but SC4S is not answering. Check `SC4S_API_URL`, the
   SC4S container status, and network connectivity.

## Upgrading

To upgrade the MCP server, rebuild the image from a newer revision of
the repository and restart the container. Configuration is
environment-based, so no data migration is required.