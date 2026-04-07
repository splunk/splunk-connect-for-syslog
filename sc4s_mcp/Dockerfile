FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.3 && \
    poetry config virtualenvs.in-project true

COPY sc4s_mcp/pyproject.toml sc4s_mcp/poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --only main

FROM python:3.11-slim

RUN groupadd --gid 10001 mcp && \
    useradd --uid 10001 --gid mcp --shell /sbin/nologin --create-home mcp

WORKDIR /app

COPY --from=builder --chown=mcp:mcp /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=mcp:mcp sc4s_mcp/ ./sc4s_mcp/
COPY --chown=mcp:mcp docs/ ./docs/
COPY --chown=mcp:mcp package/lite/etc/addons/ ./package/lite/etc/addons/

ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV SC4S_API_URL=http://sc4s:8080

EXPOSE 8000

USER mcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/sse')"]

CMD ["python", "sc4s_mcp/server.py"]
