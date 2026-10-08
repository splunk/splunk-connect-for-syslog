import asyncio

from fastmcp import Client


async def _call_sc4s_health(mcp_endpoint: str):
    async with Client(mcp_endpoint) as client:
        return await client.call_tool("sc4s_health", {})


def test_mcp_returns_sc4s_health(setup_mcp):
    result = asyncio.run(_call_sc4s_health(setup_mcp))

    assert result.is_error is False
    assert result.data is not None
    assert result.data["status"] == "healthy"
