from pathlib import Path

from fastmcp import FastMCP

from auth import build_auth_provider

mcp = FastMCP("sc4s", auth=build_auth_provider())

REPO_ROOT = Path(__file__).resolve().parent.parent