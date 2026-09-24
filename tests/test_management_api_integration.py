import datetime
import time
from pathlib import Path
from uuid import uuid4

import pytest
import requests

from .sendmessage import sendsingle
from .splunkutils import splunk_single

JOB_TIMEOUT_SECONDS = 90
JOB_POLL_INTERVAL_SECONDS = 1
PARSER_FIXTURE = (
    Path(__file__).parent / "data" / "management_api" / "app-syslog-sc4s_api_smoke.conf"
)


def _api_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def _wait_for_job(api_url: str, job_id: str) -> dict:
    deadline = time.monotonic() + JOB_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        response = requests.get(f"{api_url}/jobs/{job_id}", timeout=5)
        response.raise_for_status()
        payload = response.json()
        if payload["status"] == "success":
            return payload
        if payload["status"] == "failed":
            pytest.fail(f"configuration job {job_id} failed: {payload.get('error')}")
        time.sleep(JOB_POLL_INTERVAL_SECONDS)

    pytest.fail(
        f"configuration job {job_id} did not finish within {JOB_TIMEOUT_SECONDS}s"
    )


def _assert_accepted_job(response: requests.Response, api_url: str) -> dict:
    assert response.status_code == 202, response.text
    payload = response.json()
    assert payload["status"] == "accepted"
    assert response.headers["Location"] == f"/jobs/{payload['job_id']}"
    return _wait_for_job(api_url, payload["job_id"])


def _post_json(api_url: str, path: str, payload: dict) -> dict:
    response = requests.post(f"{api_url}{path}", json=payload, timeout=10)
    return _assert_accepted_job(response, api_url)


def _upload_parser(api_url: str, parser_name: str, parser_content: str) -> dict:
    response = requests.post(
        f"{api_url}/config/parser",
        files={"file": (parser_name, parser_content.encode("utf-8"))},
        timeout=10,
    )
    return _assert_accepted_job(response, api_url)


def _delete(api_url: str, path: str) -> dict:
    response = requests.delete(f"{api_url}{path}", timeout=10)
    return _assert_accepted_job(response, api_url)


@pytest.mark.features
def test_management_api_add_parser(setup_sc4s, setup_splunk):
    sc4s_host, ports = setup_sc4s
    api_url = _api_url(sc4s_host, ports[8080])
    parser_name = "app-syslog-sc4s_api_smoke.conf"
    parser_stem = parser_name.removesuffix(".conf")
    expected_sourcetype = "sc4s:api:parser-smoke"
    marker = f"sc4s-management-api-{uuid4()}"
    hostname = f"sc4s-api-{uuid4().hex[:12]}"
    program = "sc4s-api-smoke"

    parsers_response = requests.get(f"{api_url}/config/parsers", timeout=5)
    assert parsers_response.status_code == 200, parsers_response.text

    parser_content = PARSER_FIXTURE.read_text(encoding="utf-8")
    try:
        parser_job = _upload_parser(api_url, parser_name, parser_content)
        assert parser_job["result"] == {
            "status": "parser added successfully",
            "path": f"/etc/syslog-ng/conf.d/local/config/app_parsers/{parser_name}",
        }

        parser_response = requests.get(
            f"{api_url}/config/parser/{parser_stem}", timeout=5
        )
        parser_response.raise_for_status()
        assert parser_response.json()["content"] == parser_content

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%b %d %H:%M:%S"
        )
        message = f"<134>{timestamp} {hostname} {program}: {marker}\n"
        sendsingle(message, sc4s_host, ports[514])

        search = (
            f'search index=main "{marker}" host="{hostname}" '
            f'sourcetype="{expected_sourcetype}"'
        )
        result_count, _ = splunk_single(setup_splunk, search, attempt_limit=20)
        assert result_count == 1
    finally:
        _delete(api_url, f"/config/parser/{parser_stem}")


@pytest.mark.features
def test_management_api_metadata(setup_sc4s, setup_splunk):
    sc4s_host, ports = setup_sc4s
    api_url = _api_url(sc4s_host, ports[8080])
    parser_name = "app-syslog-sc4s_api_smoke.conf"
    parser_stem = parser_name.removesuffix(".conf")
    expected_sourcetype = "sc4s:api:metadata-smoke"
    marker = f"sc4s-management-api-{uuid4()}"
    hostname = f"sc4s-api-{uuid4().hex[:12]}"
    program = "sc4s-api-smoke"

    original_metadata = requests.get(f"{api_url}/config/metadata/splunk", timeout=5)
    original_metadata.raise_for_status()
    metadata_payload = {
        "entries": [
            {
                "key": "sc4s_api_smoke",
                "metadata": "sourcetype",
                "value": expected_sourcetype,
            }
        ]
    }
    parser_content = PARSER_FIXTURE.read_text(encoding="utf-8")

    try:
        parser_job = _upload_parser(api_url, parser_name, parser_content)
        assert parser_job["result"] == {
            "status": "parser added successfully",
            "path": f"/etc/syslog-ng/conf.d/local/config/app_parsers/{parser_name}",
        }

        metadata_job = _post_json(api_url, "/config/metadata/splunk", metadata_payload)
        assert metadata_job["result"]["entries"] == metadata_payload["entries"]

        metadata_response = requests.get(f"{api_url}/config/metadata/splunk", timeout=5)
        metadata_response.raise_for_status()
        assert metadata_response.json()["entries"] == metadata_payload["entries"]

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%b %d %H:%M:%S"
        )
        message = f"<134>{timestamp} {hostname} {program}: {marker}\n"
        sendsingle(message, sc4s_host, ports[514])

        search = (
            f'search index=main "{marker}" host="{hostname}" '
            f'sourcetype="{expected_sourcetype}"'
        )
        result_count, _ = splunk_single(setup_splunk, search, attempt_limit=20)
        assert result_count == 1
    finally:
        _delete(api_url, "/config/metadata/splunk")
        original_metadata_payload = original_metadata.json()
        if original_metadata_payload["entries"]:
            _post_json(api_url, "/config/metadata/splunk", original_metadata_payload)
        _delete(api_url, f"/config/parser/{parser_stem}")


@pytest.mark.features
def test_management_api_compliance(setup_sc4s, setup_splunk):
    sc4s_host, ports = setup_sc4s
    api_url = _api_url(sc4s_host, ports[8080])
    marker = f"sc4s-management-api-{uuid4()}"
    hostname = f"sc4s-api-{uuid4().hex[:12]}"
    program = "sc4s-api-smoke"

    original_compliance = requests.get(
        f"{api_url}/config/metadata/compliance", timeout=5
    )
    original_compliance.raise_for_status()

    compliance_payload = {
        "conf_content": (
            f'filter f_sc4s_api_smoke {{ host("{hostname}" type(string)); }};'
        ),
        "csv_content": [
            {
                "filter_name": "f_sc4s_api_smoke",
                "field_name": "fields.sc4s_api_smoke",
                "value": marker,
            }
        ],
    }
    try:
        compliance_job = _post_json(
            api_url, "/config/metadata/compliance", compliance_payload
        )
        assert compliance_job["result"] == {
            "status": "compliance metadata updated successfully"
        }
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%b %d %H:%M:%S"
        )
        message = f"<134>{timestamp} {hostname} {program}: {marker}\n"
        sendsingle(message, sc4s_host, ports[514])

        search = (
            f'search index=osnix "{marker}" host="{hostname}" '
            f'sc4s_api_smoke="{marker}"'
        )
        result_count, _ = splunk_single(setup_splunk, search, attempt_limit=20)
        assert result_count == 1
    finally:
        _delete(api_url, "/config/metadata/compliance")
        original_compliance_payload = original_compliance.json()
        if (
            original_compliance_payload["conf_content"]
            or original_compliance_payload["csv_content"]
        ):
            _post_json(
                api_url,
                "/config/metadata/compliance",
                original_compliance_payload,
            )
