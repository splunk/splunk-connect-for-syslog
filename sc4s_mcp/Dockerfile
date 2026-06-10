FROM python:3.13-alpine3.24 AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.2.1 && \
    poetry config virtualenvs.in-project true

COPY sc4s_mcp/pyproject.toml sc4s_mcp/poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --only main \
    && .venv/bin/python -m pip install --no-cache-dir --upgrade pip==26.1

FROM python:3.13-alpine3.24

RUN apk add --no-cache ca-certificates

RUN python -m pip install --no-cache-dir --upgrade pip==26.1

RUN addgroup -S -g 10001 mcp && \
    adduser -S -D -u 10001 -G mcp -s /sbin/nologin mcp

WORKDIR /app

COPY --from=builder --chown=mcp:mcp /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=mcp:mcp sc4s_mcp/ ./sc4s_mcp/
COPY --chown=mcp:mcp docs/ ./docs/
COPY --chown=mcp:mcp package/lite/etc/addons/ ./package/lite/etc/addons/
COPY --chown=mcp:mcp .agents/skills/parser-creator/ ./.agents/skills/parser-creator/

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
