from pathlib import Path

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import build_auth_provider

mcp = FastMCP("sc4s", auth=build_auth_provider())

REPO_ROOT = Path(__file__).resolve().parent.parent


@mcp.custom_route("/health", methods=["GET"])
async def health(_request: Request) -> JSONResponse:
    """Unauthenticated liveness probe for container orchestrators."""
    return JSONResponse({"status": "ok"}, status_code=200)
