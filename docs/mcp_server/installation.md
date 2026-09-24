# Installing the SC4S MCP Server

The SC4S MCP server is distributed as a container image. It can accept remote
connections over Streamable HTTP or run locally using the `stdio` transport.

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
  over `stdio` or streamable HTTP (for example: Cursor, Claude Desktop, or
  Visual Studio Code with an MCP extension).

## Prepare your SC4S instance

Before running the MCP server, make sure your SC4S instance is properly configured.

* **Enable SC4S management API** - by default SC4S API exposes only the `/health` endpoint. The configuration and metadata endpoints are **disabled**. To enable them, set `SC4S_API_MANAGEMENT_ENABLED` to `true` in your SC4S `env_file` (see
[SC4S management API](../configuration.md#sc4s-management-api-endpoints)).
* **Configure SC4S API authentication** - authentication is recommended when
  management endpoints are enabled. See
  [SC4S management API authentication](../configuration.md#sc4s-management-api-authentication).
* **Mount env_file** - some MCP management tools need to read and write SC4S's `env_file` at runtime. The `--env-file` flag alone is **not sufficient**: it only injects variables at startup and does not make the file writable inside the container. To make `env_file` accessible to the SC4S process, you need to bind-mount it into the container. If you are using systemd, follow the steps below:

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

## SC4S MCP configuration reference

The MCP server is configured through environment variables.

| Variable                    | Default                 | Description                                                                                                                                                                                                                                                                                                                  |
|-----------------------------|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `MCP_TRANSPORT`             | `http`                  | Transport mode. `http` serves both local and remote clients (default); `stdio` for local-only and test setups.                                                                                                                                                                                                               |
| `MCP_HOST`                  | `0.0.0.0`               | Bind address used in `http` mode. The default accepts connections through the container's network interfaces. |
| `MCP_PORT`                  | `8000`                  | TCP port used in `http` mode.                                                                                                                                                                                                                                                                                                |
| `MCP_LOG_LEVEL`             | `INFO`                  | Logging verbosity. Accepts standard Python log level names: `DEBUG`, `INFO`, `WARNING`, `ERROR`.                                                                                                                                                                                                                             |
| `SC4S_API_URL`              | `http://localhost:8080` | URL of the SC4S management REST API. The MCP server calls this URL for all management tools.                                                                                                                                                                                                                                 |
| `SC4S_MCP_ALLOWED_SYSLOG_PORTS` | `514,601` | Comma-separated syslog destination ports permitted for event-sending tools. Set to `*` to allow every valid port. The destination host always remains the hostname from `SC4S_API_URL`. |
| `SC4S_MCP_ALLOWED_HOSTS`     | loopback hosts          | Additional comma-separated HTTP `Host` values accepted by the MCP server. `localhost`, `127.0.0.1`, and `[::1]` are always allowed. A value without a port accepts that host on any port; include a port to restrict it. Required when clients connect using a non-loopback hostname or address. |
| `SC4S_MCP_ALLOWED_ORIGINS`   |                         | Comma-separated browser origins accepted by the MCP server, using exact `http://host[:port]` or `https://host[:port]` values. Requests without an `Origin` header, including normal native MCP clients, remain allowed. |
| `SC4S_API_TOKEN`            |                         | Bearer token sent by the MCP server to the SC4S management REST API in `Authorization: Bearer <token>`. Required when the SC4S API has authentication enabled. See [SC4S API authentication](#sc4s-api-authentication) and [Enabling auth on the SC4S API](../configuration.md#sc4s-management-api-authentication). |
| `SC4S_API_TOKEN_FILE`       |                         | Path inside the container to a file containing the SC4S API bearer token. Takes precedence over `SC4S_API_TOKEN` when set. Preferred over the env var to avoid the token appearing in process listings.                                                                                                                      |
| `SC4S_API_CA_CERT`          |                         | Path inside the container to a CA certificate used to verify an SC4S API certificate issued by a private CA. |
| `SC4S_MCP_AUTH_TOKEN`       |                         | Clients must present an auth token in `Authorization: Bearer <token>` on every request to `/mcp`. See [MCP server authentication](#mcp-server-authentication). |
| `SC4S_MCP_AUTH_TOKEN_FILE`  |                         | Path inside the container to a file containing the MCP bearer token. Takes precedence over `SC4S_MCP_AUTH_TOKEN` when set.                                                                                                                                                                                                   |
| `SC4S_MCP_TLS_CERT`         |                         | Path inside the container to a PEM-encoded server certificate (or full chain). Set together with `SC4S_MCP_TLS_KEY` to serve `/mcp` over HTTPS. See [TLS](#tls).                                                                                                                                                    |
| `SC4S_MCP_TLS_KEY`          |                         | Path inside the container to the matching PEM-encoded private key.                                                                                                                                                                                                                                                           |
| `SC4S_MCP_TLS_KEY_PASSWORD` |                         | Optional passphrase for an encrypted private key.                                                                                                                                                                                                                                                                            |

## Run the container

You can pull the latest SC4S MCP image from the registry:
`ghcr.io/splunk/splunk-connect-for-syslog/container3mcp`.

### Connect to SC4S

Set `SC4S_API_URL` to an address the MCP container can reach. If SC4S runs on
another host, use its hostname or IP address, for example
`https://sc4s.example.com:8080`.

If SC4S and the MCP server run as separate containers on the same host,
choose one of these networking options:

* With host networking, run the MCP container with `--network host` and set
  `SC4S_API_URL=http://127.0.0.1:8080`.
* With a shared container network, attach both containers to the same network
  and use the SC4S container name, for example
  `SC4S_API_URL=http://SC4S:8080`.

Create the shared network once:

```bash
docker network create sc4s-network
# or: podman network create sc4s-network
```

Add `--network sc4s-network` when starting both SC4S and the MCP server. For
the MCP container, use:

```bash
--network sc4s-network \
-e SC4S_API_URL=http://SC4S:8080
```

When SC4S uses a bridge network, publish the syslog listener ports required by
your devices. Port 8080 does not need to be published because the MCP container
can reach it over the shared network.

### Deploy for remote MCP clients

For remote access, configure an allowed hostname, bearer-token authentication,
and TLS. The example below uses `mcp.example.com` and expects its certificate
and private key in `/opt/sc4s-mcp/tls`.

Create an MCP token:

```bash
mkdir -p /opt/sc4s-mcp/secrets
python -c "import secrets; print(secrets.token_urlsafe(32))" \
  > /opt/sc4s-mcp/secrets/mcp_token
chmod 600 /opt/sc4s-mcp/secrets/mcp_token
```

Run the container:

```bash
docker run -d \
  -p 8000:8000 \
  -e SC4S_MCP_ALLOWED_HOSTS=mcp.example.com \
  -v /opt/sc4s-mcp/secrets/mcp_token:/run/secrets/sc4s_mcp_token:ro \
  -e SC4S_MCP_AUTH_TOKEN_FILE=/run/secrets/sc4s_mcp_token \
  -v /opt/sc4s-mcp/tls:/etc/sc4s-mcp/tls:ro \
  -e SC4S_MCP_TLS_CERT=/etc/sc4s-mcp/tls/server.crt \
  -e SC4S_MCP_TLS_KEY=/etc/sc4s-mcp/tls/server.key \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  ghcr.io/splunk/splunk-connect-for-syslog/container3mcp
```

Replace `docker` with `podman` when using Podman. If SC4S uses host networking
on the same Linux host, replace `-p 8000:8000` with `--network host` and set
`SC4S_API_URL=http://127.0.0.1:8080`. If both containers use `sc4s-network`,
add `--network sc4s-network` and set
`SC4S_API_URL=http://SC4S:8080`.

If the SC4S API requires authentication, add `SC4S_API_TOKEN_FILE` as shown in
[SC4S API authentication](#sc4s-api-authentication).

### Local HTTP testing

For testing with an MCP client on the container host, the endpoint can be
published on loopback without configuring TLS:

```bash
docker run -d \
  -p 127.0.0.1:8000:8000 \
  -e SC4S_API_URL=http://<SC4S_HOST>:8080 \
  --name sc4s-mcp \
  ghcr.io/splunk/splunk-connect-for-syslog/container3mcp
```

Replace `docker` with `podman` when using Podman. The local client connects to
`http://127.0.0.1:8000/mcp`.

## Host and origin validation

The HTTP transport validates every request before it reaches `/mcp` or
`/health`. By default, only the loopback hosts `localhost`, `127.0.0.1`, and
`[::1]` are accepted. Native MCP clients normally omit the `Origin` header and
continue to work without additional configuration.

For a remote deployment explicitly allow the hostname clients use:

```bash
-e SC4S_MCP_ALLOWED_HOSTS=mcp.example.com
```

Requests with any other `Host` are rejected with HTTP 421. If a browser-based
client connects directly to the MCP server, also allow its exact origin:

```bash
-e SC4S_MCP_ALLOWED_ORIGINS=https://browser.example.com
```

Origins include the scheme and, when non-default or explicitly sent, the port.
For example, `https://browser.example.com` and
`https://browser.example.com:8443` are different allowed origins. An
unlisted or malformed `Origin` is rejected with HTTP 403. Wildcard syntax is
not supported; list each host or origin explicitly.

The image ships a healthcheck that verifies the SSE endpoint is up. Check
the container status with:

```bash
docker ps   # or: podman ps
```

## SC4S API authentication

When the SC4S management REST API requires authentication, the MCP server
must present the same bearer token. Configure authentication on SC4S as
described in
[SC4S management API authentication](../configuration.md#sc4s-management-api-authentication).

Mount the file containing that same token in the MCP container and add these
options to the `docker run` or `podman run` command:

```bash
-v /opt/sc4s-mcp/secrets/sc4s_api_token:/run/secrets/sc4s_api_token:ro \
-e SC4S_API_TOKEN_FILE=/run/secrets/sc4s_api_token
```

The token file should be readable only by the account running the container:

```bash
chmod 600 /opt/sc4s-mcp/secrets/sc4s_api_token
```

You can use `SC4S_API_TOKEN` instead, but an environment variable can be
visible in container inspection output. When both token settings are empty, no
`Authorization` header is sent to the SC4S API.

If the SC4S API is served with a self-signed or private CA certificate, set `SC4S_API_CA_CERT` to the
path of the CA certificate inside the container so the MCP server can verify it.

## MCP server authentication

Token authentication between MCP clients and the SC4S MCP server
is configured with `SC4S_MCP_AUTH_TOKEN` or `SC4S_MCP_AUTH_TOKEN_FILE`.
When either setting is present, every request to `/mcp` must carry an
`Authorization: Bearer <token>` header that matches the configured value;
mismatches return HTTP 401.

Use a unique, randomly generated token of at least 32 bytes. A token file keeps
the value out of process listings and container inspection output. When both
token settings are empty, authentication is disabled.

Configure the MCP client to send the token in the `Authorization` header
on every request to `/mcp` (see
[Generic MCP client configuration](#generic-mcp-client-configuration)
below).

## TLS

Remote connections should use TLS. Set `SC4S_MCP_TLS_CERT` and
`SC4S_MCP_TLS_KEY` to serve `/mcp` and `/health` over HTTPS. If only one is
set, the server refuses to start.

When both settings are empty, the server uses HTTP. TLS can also be terminated
by a reverse proxy. In that configuration, publish the container on host
loopback with `-p 127.0.0.1:8000:8000` and have the proxy forward requests to
that address.

If the private key is encrypted, also pass `-e SC4S_MCP_TLS_KEY_PASSWORD="$PASS"`.

When using a self-signed certificate, install the issuing CA in the operating
system or MCP client trust store.

## Generic MCP client configuration

Most MCP clients accept one of two connection styles. Consult your
client's documentation for the exact configuration file and its location;
the shape of the configuration is typically the same across clients.

**Remote endpoint (Streamable HTTP)**: the client connects to the single
`/mcp` HTTP endpoint exposed by the server. Provide:

* a `url` pointing at `https://<MCP_HOST>:8000/mcp`,
* a `headers` map carrying `Authorization: Bearer <TOKEN>`, plus any other
  headers required by your deployment.

For example, the corresponding `.cursor/mcp.json` for Cursor on a
remote workstation is:

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

**Local process (stdio)**: the client launches the server as a child
process and communicates via standard input/output. Provide:

* a `command` to execute (for example `docker` or `podman`),
* an `args` array that starts the MCP server,
* optional environment variables (`SC4S_API_URL`, `MCP_TRANSPORT=stdio`).

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

To upgrade the MCP server, pull a newer image and recreate the container with
the same configuration options. No data migration is required.

Docker:

```bash
docker stop sc4s-mcp && docker rm sc4s-mcp
docker pull ghcr.io/splunk/splunk-connect-for-syslog/container3mcp
```

Podman:

```bash
podman stop sc4s-mcp && podman rm sc4s-mcp
podman pull ghcr.io/splunk/splunk-connect-for-syslog/container3mcp
```

Then run the same `docker run` or `podman run` command used for the previous
version.
