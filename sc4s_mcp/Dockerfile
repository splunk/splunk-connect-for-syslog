FROM python:3.15-alpine3.24@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.4.1 && \
    poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.options.no-pip true

COPY sc4s_mcp/pyproject.toml sc4s_mcp/poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --only main

FROM python:3.15-alpine3.24@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb

ARG VERSION

# Require the Alpine fix for CVE-2026-85091
RUN apk add --no-cache --upgrade bash ca-certificates 'zlib>=1.3.2-r1'

# Runtime package installation is unnecessary; pip bundles vulnerable libraries.
RUN python -m pip uninstall --yes pip

RUN addgroup -S -g 10001 mcp && \
    adduser -S -D -u 10001 -G mcp -s /sbin/nologin mcp

WORKDIR /app

COPY --from=builder --chown=mcp:mcp /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV SC4S_MCP_VERSION=${VERSION}

COPY --chown=mcp:mcp sc4s_mcp/ ./sc4s_mcp/
COPY --chown=mcp:mcp docs/ ./docs/
COPY --chown=mcp:mcp package/shared/addons/ ./package/shared/addons/
COPY --chown=mcp:mcp skills/parser-creator/ ./skills/parser-creator/
COPY --chown=mcp:mcp configuration-tool.sh ./configuration-tool.sh

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
