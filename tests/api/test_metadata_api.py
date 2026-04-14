from unittest.mock import patch
import pytest
from package.sbin.api import app

@pytest.fixture
def ctx_dir(tmp_path):
    """Patch all file paths to use a temp directory."""
    with patch("metadata_api.CONTEXT_DIR", tmp_path), \
         patch("metadata_api.SPLUNK_METADATA_CSV", tmp_path / "splunk_metadata.csv"), \
         patch("metadata_api.COMPLIANCE_CONF", tmp_path / "compliance.conf"), \
         patch("metadata_api.COMPLIANCE_CSV", tmp_path / "compliance.csv"):
        yield tmp_path

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_splunk_metadata(client, ctx_dir):
    csv_file = ctx_dir / "splunk_metadata.csv"
    csv_file.write_text("juniper_netscreen,index,ns_index\ncisco_asa,sourcetype,cisco:asa\n")

    resp = client.get("/config/metadata/splunk")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["entries"]) == 2
    assert data["entries"][0] == {"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}
    assert data["entries"][1] == {"key": "cisco_asa", "metadata": "sourcetype", "value": "cisco:asa"}

def test_get_splunk_metadata_empty_file(client, ctx_dir):
    csv_file = ctx_dir / "splunk_metadata.csv"
    csv_file.write_text("")

    resp = client.get("/config/metadata/splunk")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["entries"]) == 0

@patch("metadata_api._apply_with_rollback")
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
    entries = [{"key": "juniper_netscreen", "metadata": "badfield", "value": "ns_index"}]

    resp = client.post("/config/metadata/splunk", json={"entries": entries})

    assert resp.status_code == 400
    assert "Invalid metadata field" in resp.get_json()["message"]

def test_set_splunk_metadata_no_body(client, ctx_dir):
    resp = client.post("/config/metadata/splunk")

    assert resp.status_code == 400
    assert "entries" in resp.get_json()["message"]

@patch("metadata_api._apply_with_rollback")
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
