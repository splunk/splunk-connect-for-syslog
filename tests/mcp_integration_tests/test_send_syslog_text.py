import asyncio
import datetime
import uuid

from fastmcp import Client

from tests.mcp_integration_tests.utils import _call_tool
from tests.splunkutils import splunk_single


async def _exercise_send_syslog_text(mcp_endpoint: str, splunk) -> None:
    suffix = uuid.uuid4().hex
    marker = f"sc4s-mcp-send-{suffix}"
    hostname = f"sc4s-mcp-{suffix[:12]}"
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%b %d %H:%M:%S"
    )
    event = f"<111>{timestamp} {hostname} cron[12345]: {marker}"

    async with Client(mcp_endpoint) as client:
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
        f'search index=osnix "{marker}" host="{hostname}" '
        'sourcetype="nix:syslog"'
    )
    result_count, _ = splunk_single(
        splunk,
        search,
        attempt_limit=20,
    )
    assert result_count == 1


def test_mcp_send_syslog_text_reaches_splunk(setup_mcp, setup_splunk):
    asyncio.run(_exercise_send_syslog_text(setup_mcp, setup_splunk))
