FROM python:3.15-alpine3.24@sha256:0f9552bb28711333da16915ec146f5e6bb44a7fdac9ced15dc17c2e0206346dd AS builder

WORKDIR /app

RUN pip install --no-cache-dir --only-binary :all: poetry==2.4.1 && \
    poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.options.no-pip true

COPY sc4s_mcp/pyproject.toml sc4s_mcp/poetry.lock* ./
RUN POETRY_INSTALLER_ONLY_BINARY=:all: poetry install --no-interaction --no-ansi --only main

FROM python:3.15-alpine3.24@sha256:0f9552bb28711333da16915ec146f5e6bb44a7fdac9ced15dc17c2e0206346dd

ARG VERSION

# Require the Alpine fix for CVE-2026-85091.
# Runtime package installation is unnecessary; pip bundles vulnerable libraries.
RUN apk add --no-cache --upgrade bash ca-certificates 'zlib>=1.3.2-r1' && \
    python -m pip uninstall --yes pip && \
    addgroup -S -g 10001 mcp && \
    adduser -S -D -u 10001 -G mcp -s /sbin/nologin mcp

WORKDIR /app

# Application files stay root-owned so the runtime user cannot modify them.
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV SC4S_MCP_VERSION=${VERSION}

COPY sc4s_mcp/ ./sc4s_mcp/
COPY docs/ ./docs/
COPY package/shared/addons/ ./package/shared/addons/
COPY skills/create-parser/ ./skills/create-parser/
COPY skills/manage-sc4s-parsers/ ./skills/manage-sc4s-parsers/
COPY skills/manage-sc4s-splunk-metadata/ ./skills/manage-sc4s-splunk-metadata/
COPY skills/sc4s-guided-configuration/ ./skills/sc4s-guided-configuration/
COPY skills/sc4s-send-syslog/ ./skills/sc4s-send-syslog/
COPY skills/troubleshoot-sc4s/ ./skills/troubleshoot-sc4s/
COPY configuration-tool.sh ./configuration-tool.sh

ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV SC4S_API_URL=http://localhost:8080

EXPOSE 8000

USER mcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "/app/sc4s_mcp/health_probe.py"]

WORKDIR /app/sc4s_mcp

CMD ["python", "server.py"]
