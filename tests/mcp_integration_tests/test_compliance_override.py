import asyncio
import datetime
import uuid

from fastmcp import Client

from tests.mcp_integration_tests.utils import (
    _call_tool,
    _submit_config_change,
)
from tests.splunkutils import splunk_single


async def _exercise_compliance_override_tools(mcp_endpoint: str, splunk) -> None:
    suffix = uuid.uuid4().hex
    marker = f"sc4s-mcp-compliance-{suffix}"
    hostname = f"sc4s-mcp-{suffix[:12]}"
    filter_name = f"f_sc4s_mcp_compliance_{suffix}"
    conf_content = (
        f'filter {filter_name} {{ host("{hostname}" type(string)); }};'
    )
    csv_content = [
        {
            "filter_name": filter_name,
            "field_name": "fields.sc4s_mcp_compliance",
            "value": marker,
        }
    ]
    override_set = False
    override_deleted = False

    async with Client(mcp_endpoint) as client:
        initial = await _call_tool(client, "get_compliance_overrides")
        original_conf = initial["conf_content"]
        original_csv = initial["csv_content"]

        try:
            set_job = await _submit_config_change(
                client,
                "set_compliance_override",
                conf_content=conf_content,
                csv_content=csv_content,
            )
            override_set = True
            assert (
                set_job["result"]["status"]
                == "compliance metadata updated successfully"
            )

            updated = await _call_tool(client, "get_compliance_overrides")
            assert updated["conf_content"].strip() == conf_content
            assert updated["csv_content"] == csv_content

            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%b %d %H:%M:%S"
            )
            event = f"<111>{timestamp} {hostname} cron[12345]: {marker}"
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
                'sourcetype="nix:syslog" '
                f'sc4s_mcp_compliance="{marker}"'
            )
            result_count, _ = await asyncio.to_thread(
                splunk_single,
                splunk,
                search,
                attempt_limit=20,
            )
            assert result_count == 1

            delete_job = await _submit_config_change(
                client,
                "delete_compliance_override",
            )
            override_deleted = True
            assert (
                delete_job["result"]["status"]
                == "compliance metadata cleared successfully"
            )

            cleared = await _call_tool(client, "get_compliance_overrides")
            assert cleared["conf_content"] == ""
            assert cleared["csv_content"] == []
        finally:
            if override_set:
                if original_conf or original_csv:
                    restore_job = await _submit_config_change(
                        client,
                        "set_compliance_override",
                        conf_content=original_conf,
                        csv_content=original_csv,
                    )
                    assert (
                        restore_job["result"]["status"]
                        == "compliance metadata updated successfully"
                    )
                elif not override_deleted:
                    cleanup_job = await _submit_config_change(
                        client,
                        "delete_compliance_override",
                    )
                    assert (
                        cleanup_job["result"]["status"]
                        == "compliance metadata cleared successfully"
                    )

            restored = await _call_tool(client, "get_compliance_overrides")
            assert restored["conf_content"].strip() == original_conf.strip()
            assert restored["csv_content"] == original_csv


def test_mcp_compliance_override_set_verify_delete(setup_mcp, setup_splunk):
    asyncio.run(_exercise_compliance_override_tools(setup_mcp, setup_splunk))
