import asyncio
import datetime
import uuid

from fastmcp import Client

from tests.splunkutils import splunk_single


JOB_TIMEOUT_SECONDS = 90
JOB_POLL_INTERVAL_SECONDS = 1


async def _call_tool(client: Client, name: str, arguments: dict | None = None) -> dict:
    result = await client.call_tool(name, arguments or {})
    assert result.is_error is False, result
    assert result.data is not None, result
    return result.data


async def _wait_for_job(client: Client, job_id: str) -> dict:
    deadline = asyncio.get_running_loop().time() + JOB_TIMEOUT_SECONDS

    while asyncio.get_running_loop().time() < deadline:
        job = await _call_tool(client, "get_job_status", {"job_id": job_id})
        if job["status"] == "success":
            return job
        if job["status"] == "failed":
            raise AssertionError(f"configuration job {job_id} failed: {job}")
        await asyncio.sleep(JOB_POLL_INTERVAL_SECONDS)

    raise AssertionError(f"configuration job {job_id} did not finish in time")


async def _submit_metadata_change(client: Client, tool_name: str, **arguments) -> dict:
    response = await _call_tool(client, tool_name, arguments)
    assert response.get("status") == "accepted", response
    assert response.get("job_id"), response
    return await _wait_for_job(client, response["job_id"])


def _smoke_parser(suffix: str) -> tuple[str, str, str]:
    app_name = f"sc4s_mcp_meta_{suffix}"
    parser_name = f"app-syslog-{app_name}.conf"
    program = f"sc4s-mcp-meta-{suffix}"
    content = f'''block parser app-syslog-{app_name}() {{
    channel {{
        rewrite {{
            r_set_splunk_dest_default(
                index("main")
                sourcetype("sc4s:mcp:metadata-default")
                vendor("sc4s")
                product("mcp_meta_{suffix}")
            );
        }};
    }};
}};

application {app_name}[sc4s-network-source] {{
    filter {{ program("{program}" type(string) flags(prefix)); }};
    parser {{ app-syslog-{app_name}(); }};
}};
'''
    return parser_name, program, content


async def _exercise_splunk_metadata_tools(mcp_endpoint: str, splunk) -> None:
    async with Client(mcp_endpoint) as client:
        initial = await _call_tool(client, "get_splunk_metadata")
        original_entries = initial["entries"]
        suffix = uuid.uuid4().hex
        parser_name, program, parser_content = _smoke_parser(suffix)
        marker = f"sc4s-mcp-metadata-{suffix}"
        hostname = f"sc4s-mcp-{suffix[:12]}"
        expected_sourcetype = f"sc4s:mcp:metadata-{suffix}"
        test_entry = {
            "key": f"sc4s_mcp_meta_{suffix}",
            "metadata": "sourcetype",
            "value": expected_sourcetype,
        }
        expected_entries = [*original_entries, test_entry]
        parser_added = False

        try:
            await _submit_metadata_change(
                client,
                "add_parser",
                filename=parser_name,
                content=parser_content,
            )
            parser_added = True

            await _submit_metadata_change(
                client, "set_splunk_metadata", entries=expected_entries
            )

            updated = await _call_tool(client, "get_splunk_metadata")
            assert updated["entries"] == expected_entries

            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%b %d %H:%M:%S"
            )
            event = f"<134>{timestamp} {hostname} {program}: {marker}"
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
                f'sourcetype="{expected_sourcetype}"'
            )
            result_count, _ = await asyncio.to_thread(
                splunk_single, splunk, search, attempt_limit=20
            )
            assert result_count == 1

            await _submit_metadata_change(client, "delete_splunk_metadata")

            cleared = await _call_tool(client, "get_splunk_metadata")
            assert cleared["entries"] == []
        finally:
            try:
                if parser_added:
                    await _submit_metadata_change(
                        client, "delete_parser", name=parser_name
                    )
            finally:
                # set_splunk_metadata is a full replacement, so restore live state.
                if original_entries:
                    await _submit_metadata_change(
                        client, "set_splunk_metadata", entries=original_entries
                    )
                else:
                    await _submit_metadata_change(client, "delete_splunk_metadata")

            restored = await _call_tool(client, "get_splunk_metadata")
            assert restored["entries"] == original_entries


def test_mcp_splunk_metadata_get_set_verify_delete_verify(setup_mcp, setup_splunk):
    asyncio.run(_exercise_splunk_metadata_tools(setup_mcp, setup_splunk))
