from unittest.mock import patch
import pytest
from package.sbin.api import app


@pytest.fixture
def ctx_dir(tmp_path):
    """Patch all file paths to use a temp directory."""
    with (
        patch("metadata_api.SPLUNK_METADATA_CSV", tmp_path / "splunk_metadata.csv"),
        patch("metadata_api.COMPLIANCE_CONF", tmp_path / "compliance.conf"),
        patch("metadata_api.COMPLIANCE_CSV", tmp_path / "compliance.csv"),
    ):
        yield tmp_path


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# GET /config/metadata/splunk
# ---------------------------------------------------------------------------


def test_get_splunk_metadata(client, ctx_dir):
    csv_file = ctx_dir / "splunk_metadata.csv"
    csv_file.write_text(
        "juniper_netscreen,index,ns_index\ncisco_asa,sourcetype,cisco:asa\n"
    )

    resp = client.get("/config/metadata/splunk")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["entries"]) == 2
    assert data["entries"][0] == {
        "key": "juniper_netscreen",
        "metadata": "index",
        "value": "ns_index",
    }
    assert data["entries"][1] == {
        "key": "cisco_asa",
        "metadata": "sourcetype",
        "value": "cisco:asa",
    }


def test_get_splunk_metadata_empty_file(client, ctx_dir):
    csv_file = ctx_dir / "splunk_metadata.csv"
    csv_file.write_text("")

    resp = client.get("/config/metadata/splunk")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["entries"]) == 0


# ---------------------------------------------------------------------------
# POST /config/metadata/splunk
# ---------------------------------------------------------------------------


@patch("metadata_api.apply_with_rollback")
def test_set_splunk_metadata(mock_apply, client, ctx_dir):
    entries = [{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}]

    resp = client.post("/config/metadata/splunk", json={"entries": entries})

    assert resp.status_code == 200
    assert resp.get_json()["status"] == "metadata updated successfully"
    mock_apply.assert_called_once()


def test_set_splunk_metadata_missing_keys(client, ctx_dir):
    entries = [{"key": "juniper_netscreen", "value": "ns_index"}]

    resp = client.post("/config/metadata/splunk", json={"entries": entries})

    assert resp.status_code == 400
    assert "must have" in resp.get_json()["message"]


def test_set_splunk_metadata_invalid_meta(client, ctx_dir):
    entries = [
        {"key": "juniper_netscreen", "metadata": "badfield", "value": "ns_index"}
    ]

    resp = client.post("/config/metadata/splunk", json={"entries": entries})

    assert resp.status_code == 400
    assert "Invalid metadata field" in resp.get_json()["message"]


def test_set_splunk_metadata_no_body(client, ctx_dir):
    resp = client.post("/config/metadata/splunk")

    assert resp.status_code == 400
    assert "entries" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# DELETE /config/metadata/splunk
# ---------------------------------------------------------------------------


@patch("metadata_api.apply_with_rollback")
def test_delete_metadata(mock_apply, client, ctx_dir):
    csv_file = ctx_dir / "splunk_metadata.csv"
    csv_file.write_text("juniper_netscreen,index,ns_index\n")

    resp = client.delete("/config/metadata/splunk")

    assert resp.status_code == 200
    assert "cleared successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


def test_delete_metadata_no_file(client, ctx_dir):
    resp = client.delete("/config/metadata/splunk")

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# GET /config/metadata/compliance
# ---------------------------------------------------------------------------


def test_get_compliance(client, ctx_dir):
    conf_file = ctx_dir / "compliance.conf"
    csv_file = ctx_dir / "compliance.csv"
    conf_file.write_text('filter f_pci { host("pci-*" type(glob)) };\n')
    csv_file.write_text("f_pci,.splunk.index,pci_idx\n")

    resp = client.get("/config/metadata/compliance")

    assert resp.status_code == 200
    data = resp.get_json()
    assert "f_pci" in data["conf_content"]
    assert len(data["csv_content"]) == 1
    assert data["csv_content"][0] == {
        "filter_name": "f_pci",
        "field_name": ".splunk.index",
        "value": "pci_idx",
    }


def test_get_compliance_no_files(client, ctx_dir):
    resp = client.get("/config/metadata/compliance")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["conf_content"] == ""
    assert data["csv_content"] == []


# ---------------------------------------------------------------------------
# POST /config/metadata/compliance
# ---------------------------------------------------------------------------


@patch("metadata_api.apply_with_rollback")
def test_set_compliance(mock_apply, client, ctx_dir):
    payload = {
        "conf_content": 'filter f_pci { host("pci-*" type(glob)) };',
        "csv_content": [
            {"filter_name": "f_pci", "field_name": ".splunk.index", "value": "pci_idx"}
        ],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 200
    assert "compliance metadata updated successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


@patch("metadata_api.apply_with_rollback")
def test_set_compliance_conf_only(mock_apply, client, ctx_dir):
    payload = {
        "conf_content": 'filter f_pci { host("pci-*" type(glob)) };',
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 200
    mock_apply.assert_called_once()


@patch("metadata_api.apply_with_rollback")
def test_set_compliance_csv_only(mock_apply, client, ctx_dir):
    payload = {
        "csv_content": [
            {"filter_name": "f_pci", "field_name": ".splunk.index", "value": "pci_idx"}
        ],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 200
    mock_apply.assert_called_once()


def test_set_compliance_no_body(client, ctx_dir):
    resp = client.post("/config/metadata/compliance")

    assert resp.status_code == 400
    assert "JSON body required" in resp.get_json()["message"]


def test_set_compliance_empty_payload(client, ctx_dir):
    resp = client.post(
        "/config/metadata/compliance", json={"conf_content": "", "csv_content": []}
    )

    assert resp.status_code == 400
    assert "No conf_content or csv_content" in resp.get_json()["message"]


def test_set_compliance_missing_csv_keys(client, ctx_dir):
    payload = {
        "csv_content": [{"filter_name": "f_pci", "value": "pci_idx"}],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 400
    assert "must have" in resp.get_json()["message"]


def test_set_compliance_invalid_field_name(client, ctx_dir):
    payload = {
        "csv_content": [
            {"filter_name": "f_pci", "field_name": "bad_field", "value": "val"}
        ],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 400
    assert "Invalid field_name" in resp.get_json()["message"]


def test_set_compliance_orphaned_filter(client, ctx_dir):
    payload = {
        "conf_content": 'filter f_pci { host("pci-*" type(glob)) };',
        "csv_content": [
            {
                "filter_name": "f_nonexistent",
                "field_name": ".splunk.index",
                "value": "val",
            }
        ],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 400
    assert "not defined in conf_content" in resp.get_json()["message"]


@patch("metadata_api.apply_with_rollback", side_effect=RuntimeError("restart failed"))
def test_set_compliance_rollback_on_failure(mock_apply, client, ctx_dir):
    payload = {
        "conf_content": 'filter f_pci { host("pci-*" type(glob)) };',
        "csv_content": [
            {"filter_name": "f_pci", "field_name": ".splunk.index", "value": "pci_idx"}
        ],
    }

    resp = client.post("/config/metadata/compliance", json=payload)

    assert resp.status_code == 500
    assert "restart failed" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# DELETE /config/metadata/compliance
# ---------------------------------------------------------------------------


@patch("metadata_api.apply_with_rollback")
def test_delete_compliance(mock_apply, client, ctx_dir):
    (ctx_dir / "compliance.conf").write_text("filter f_pci {};\n")
    (ctx_dir / "compliance.csv").write_text("f_pci,.splunk.index,pci_idx\n")

    resp = client.delete("/config/metadata/compliance")

    assert resp.status_code == 200
    assert "cleared successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


@patch("metadata_api.apply_with_rollback")
def test_delete_compliance_conf_only(mock_apply, client, ctx_dir):
    (ctx_dir / "compliance.conf").write_text("filter f_pci {};\n")

    resp = client.delete("/config/metadata/compliance")

    assert resp.status_code == 200
    mock_apply.assert_called_once()


def test_delete_compliance_no_files(client, ctx_dir):
    resp = client.delete("/config/metadata/compliance")

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["message"]
