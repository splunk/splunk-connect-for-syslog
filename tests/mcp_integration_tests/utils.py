import asyncio

from fastmcp import Client


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


async def _submit_config_change(client: Client, tool_name: str, **arguments) -> dict:
    response = await _call_tool(client, tool_name, arguments)
    assert response.get("status") == "accepted", response
    assert response.get("job_id"), response
    return await _wait_for_job(client, response["job_id"])
