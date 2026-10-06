import asyncio
import uuid

from fastmcp import Client

from tests.mcp_integration_tests.test_splunk_metadata import (
    _call_tool,
    _submit_metadata_change,
)


async def _exercise_env_tools(mcp_endpoint: str) -> None:
    async with Client(mcp_endpoint) as client:
        initial = await _call_tool(client, "get_env")
        if initial.get("status") == "error":
            assert initial.get("http_status") == 404, initial
            assert initial.get("message") == "env_file not found", initial
            await _submit_metadata_change(
                client,
                "set_env",
                env_file_content="# MCP integration test baseline\n",
            )
            initial = await _call_tool(client, "get_env")

        original_content = initial["content"]
        separator = (
            "" if not original_content or original_content.endswith("\n") else "\n"
        )
        updated_content = (
            f"{original_content}{separator}"
            f"SC4S_MCP_INTEGRATION_TEST={uuid.uuid4().hex}\n"
        )

        try:
            job = await _submit_metadata_change(
                client,
                "set_env",
                env_file_content=updated_content,
            )
            assert job["result"]["status"] == "env_file updated successfully"

            updated = await _call_tool(client, "get_env")
            assert updated["content"] == updated_content
        finally:
            await _submit_metadata_change(
                client,
                "set_env",
                env_file_content=original_content,
            )
            restored = await _call_tool(client, "get_env")
            assert restored["content"] == original_content


def test_mcp_env_get_set_verify_restore(setup_mcp):
    asyncio.run(_exercise_env_tools(setup_mcp))
