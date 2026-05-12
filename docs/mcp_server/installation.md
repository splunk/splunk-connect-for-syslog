# Installing the SC4S MCP Server

The SC4S MCP server is distributed as a container image. It can be run on
your local workstation for use with a local AI assistant (using the
`stdio` transport), or on a shared host, such as the same machine as your
SC4S instance, where remote assistants and agents connect to it over the
streamable HTTP.
!!! note "No host commands are executed"
    Regardless of how you run the container, the MCP server itself never
    runs commands outside the container. See
    [Security model](index.md#security-model).

## Prerequisites

SC4S MCP server is currently available only for Podman or Docker runtimes.

* A running SC4S instance exposing the management REST API (default port
  `8080`).
* Docker or Podman on the host where the MCP server will run.
* An MCP-compatible AI assistant or agent that can connect to the server
  over `stdio` or streamable HTTP (for example, Cursor, Claude Desktop, or
  Visual Studio Code with an MCP extension).

## Configuration reference

The MCP server is configured through environment variables.

| Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` (CLI) / `http` (container) | Transport mode: `stdio` for local clients, `http` for remote clients. |
| `MCP_HOST` | `0.0.0.0` | Bind address used in `http` mode. |
| `MCP_PORT` | `8000` | TCP port used in `http` mode. |
| `SC4S_API_URL` | `http://localhost:8080` | URL of the SC4S management REST API. The MCP server calls this URL for all management tools. |
| `SC4S_MCP_AUTH_TOKEN` | _unset_ (auth disabled) | Clients must present auth token in `Authorization: Bearer <token>` on every request to `/mcp`. See [Authentication](#authentication-optional). |
| `SC4S_MCP_TLS_CERT` | _unset_ (TLS disabled) | Path inside the container to a PEM-encoded server certificate (or full chain). Set together with `SC4S_MCP_TLS_KEY` to serve `/mcp` over HTTPS. See [TLS](#tls-optional). |
| `SC4S_MCP_TLS_KEY` | _unset_ (TLS disabled) | Path inside the container to the matching PEM-encoded private key. |
| `SC4S_MCP_TLS_KEY_PASSWORD` | _unset_ | Optional passphrase for an encrypted private key. |

## Build the image

The Dockerfile is part of the SC4S repository. Build from the repository
root so that the `docs/`, `package/lite/etc/addons/`, and
`.agents/skills/parser-creator/` directories are available to the build
context.

Docker:

```bash
docker build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
```

Podman:

```bash
podman build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
```

## Run the container

The examples below assume the SC4S container is reachable at
`http://<SC4S_HOST>:8080`. If SC4S runs on the same host, use
`--network host` and point `SC4S_API_URL` to `http://127.0.0.1:8080`.

Docker:

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

Podman (locally built images are stored under the `localhost/` prefix):

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

```bash
docker ps   # or: podman ps
```

## Authentication (optional)

Token authentication between MCP clients and the SC4S MCP server
is **opt-in** and controlled by a single environment variable on the
server. When `SC4S_MCP_AUTH_TOKEN` is unset or empty, authentication is
disabled. When it is set, every request to `/mcp` must carry an
`Authorization: Bearer <token>` header that matches the configured value;
mismatches return HTTP 401.

Generate a strong random token (>= 32 bytes recommended) and pass it to
the container at runtime:

```bash
TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

docker run -d \
  -p 8000:8000 \
  -e SC4S_MCP_AUTH_TOKEN="$TOKEN" \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  sc4s-mcp
```

Configure the MCP client to send the token in the `Authorization` header
on every request to `/mcp` (see
[Generic MCP client configuration](#generic-mcp-client-configuration)
below).

## TLS

TLS for the Streamable HTTP transport is **opt-in** and controlled by
two environment variables on the server. When both `SC4S_MCP_TLS_CERT`
and `SC4S_MCP_TLS_KEY` are unset, the server listens on plaintext HTTP.
When both are set, the server serves `/mcp` and `/health` over HTTPS
using uvicorn's TLS terminator (TLS 1.2, TLS 1.3). If only one is set,
the server **refuses to start**. 

### Generate a certificate for testing

For development or internal trials only, generate a self-signed cert:

```bash
mkdir -p /opt/sc4s-mcp/tls
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -subj "/CN=<MCP_HOST>" \
  -keyout /opt/sc4s-mcp/tls/server.key \
  -out    /opt/sc4s-mcp/tls/server.crt
chmod 600 /opt/sc4s-mcp/tls/server.key
```

### Run the container with TLS enabled

Mount the directory holding the cert/key into the container and point
the env vars at the in-container paths:

```bash
TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

docker run -d \
  -p 8000:8000 \
  -v /opt/sc4s-mcp/tls:/etc/sc4s-mcp/tls:ro \
  -e SC4S_MCP_TLS_CERT=/etc/sc4s-mcp/tls/server.crt \
  -e SC4S_MCP_TLS_KEY=/etc/sc4s-mcp/tls/server.key \
  -e SC4S_MCP_AUTH_TOKEN="$TOKEN" \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  sc4s-mcp
```

If the private key is encrypted, also pass
`-e SC4S_MCP_TLS_KEY_PASSWORD="$PASS"`. The passphrase is never logged.

### Configure the client

Point the MCP client at the `https://` URL and keep the bearer token
header when authentication is enabled. Cursor example:

```json
{
  "mcpServers": {
    "sc4s": {
      "url": "https://<MCP_HOST>:8000/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

Note that when using a self-signed certificate, it may be necessary to install
the issuing CA in the OS or client trust store, as some MCP clients refuse untrusted
certificates by default.

## Prepare your SC4S instance

Some MCP management tools (e.g. `sc4s_set_env`, `sc4s_get_env`)
need to read and write SC4S's `env_file` at runtime. The `--env-file`
Docker/Podman flag alone is **not sufficient**: it only injects variables at
startup and does not make the file visible inside the container.
To make `env_file` accessible to the SC4S process, you need to bind-mount it
into the container. If you are using systemd, follow the steps below:

1. Add a new environment variable to the service file (by default located at `/lib/systemd/system/sc4s.service`):
```
Environment="SC4S_ENV_FILE_MOUNT=/opt/sc4s/env_file:/opt/sc4s/env_file:z"
```
2. Add `-v $SC4S_ENV_FILE_MOUNT` to your `ExecStart` alongside the other `-v` flags:
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
3. Reload and restart the systemd service:
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

**Remote endpoint (Streamable HTTP)**: the client connects to the single
`/mcp` HTTP endpoint exposed by the server. Provide:

* a `url` pointing at `http://<MCP_HOST>:8000/mcp` (or
  `https://<MCP_HOST>:8000/mcp` when [TLS](#tls-optional) is enabled on
  the server),
* a `headers` map carrying `Authorization: Bearer <TOKEN>` when
  [bearer-token auth](#authentication-optional) is enabled on the server,
  plus any other headers required by your deployment.

For example, the corresponding `.cursor/mcp.json` for Cursor on a
remote workstation is:

```json
{
  "mcpServers": {
    "sc4s": {
      "url": "http://<MCP_HOST>:8000/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

Omit the `headers` block when the server is running without
`SC4S_MCP_AUTH_TOKEN`.

## Verify the installation

1. Confirm the container is running: `docker ps` or `podman ps`.
2. Confirm the MCP client sees the server. Most clients list available
   MCP servers in a dedicated panel or on startup.
3. From the assistant, call the `sc4s_health` tool. A healthy instance
   returns a status payload from the SC4S management API. An error like
   `"SC4S instance unreachable at http://..."` means the MCP server
   could reach out but SC4S is not answering. Check `SC4S_API_URL`, the
   SC4S container status, and network connectivity.

## Upgrading

To upgrade the MCP server, rebuild the image from a newer revision of
the repository and restart the container. Configuration is
environment-based, so no data migration is required.

Docker:

```bash
docker stop sc4s-mcp && docker rm sc4s-mcp
docker build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
docker run -d \
  -p 8000:8000 \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  sc4s-mcp
```

Podman:

```bash
podman stop sc4s-mcp && podman rm sc4s-mcp
podman build -t sc4s-mcp -f sc4s_mcp/Dockerfile .
podman run -d \
  -p 8000:8000 \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  localhost/sc4s-mcp
```