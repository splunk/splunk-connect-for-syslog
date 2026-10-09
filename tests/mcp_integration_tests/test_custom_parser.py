import asyncio
import datetime
import uuid
from pathlib import Path

from fastmcp import Client

from tests.mcp_integration_tests.utils import (
    _call_tool,
    _submit_config_change,
)
from tests.splunkutils import splunk_single


PARSER_FIXTURE = (
    Path(__file__).parents[1]
    / "data"
    / "management_api"
    / "app-syslog-sc4s_api_smoke.conf"
)


async def _exercise_custom_parser_tools(mcp_endpoint: str, splunk) -> None:
    parser_name = PARSER_FIXTURE.name
    parser_stem = parser_name.removesuffix(".conf")
    parser_content = PARSER_FIXTURE.read_text(encoding="utf-8")
    suffix = uuid.uuid4().hex
    marker = f"sc4s-mcp-parser-{suffix}"
    hostname = f"sc4s-mcp-{suffix[:12]}"
    parser_added = False

    async with Client(mcp_endpoint) as client:
        initial = await _call_tool(client, "list_custom_parsers")
        assert parser_name not in initial["parsers"]

        try:
            add_job = await _submit_config_change(
                client,
                "add_parser",
                filename=parser_name,
                content=parser_content,
            )
            parser_added = True
            assert add_job["result"]["status"] == "parser added successfully"

            deployed = await _call_tool(
                client,
                "get_custom_parser",
                {"name": parser_stem},
            )
            assert deployed["name"] == parser_name
            assert deployed["content"] == parser_content

            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%b %d %H:%M:%S"
            )
            event = f"<134>{timestamp} {hostname} sc4s-api-smoke: {marker}"
            send_result = await _call_tool(
                client,
                "send_syslog_text",
                {
                    "text": event,
                    "protocol": "tcp",
                    "port": 514,
                    "framing": "newline",
                },
            )
            assert send_result["status"] == "ok", send_result
            assert send_result["sent"] == 1, send_result

            search = (
                f'search index=main "{marker}" host="{hostname}" '
                'sourcetype="sc4s:api:parser-smoke"'
            )
            result_count, _ = splunk_single(
                splunk,
                search,
                attempt_limit=20,
            )
            assert result_count == 1
        finally:
            if parser_added:
                delete_job = await _submit_config_change(
                    client,
                    "delete_parser",
                    name=parser_stem,
                )
                assert (
                    delete_job["result"]["status"]
                    == "parser deleted successfully"
                )

            final = await _call_tool(client, "list_custom_parsers")
            assert sorted(final["parsers"]) == sorted(initial["parsers"])


def test_mcp_custom_parser_add_verify_send_delete(setup_mcp, setup_splunk):
    asyncio.run(_exercise_custom_parser_tools(setup_mcp, setup_splunk))
