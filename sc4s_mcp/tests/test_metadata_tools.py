from unittest.mock import patch

from tools.metadata_tools import (
    delete_compliance_override,
    delete_splunk_metadata,
    get_compliance_overrides,
    get_splunk_metadata,
    set_compliance_override,
    set_splunk_metadata,
)


@patch("tools.metadata_tools.sc4s_request")
def test_get_splunk_metadata(mock_sc4s_request):
    get_splunk_metadata()

    mock_sc4s_request.assert_called_once_with(
        "get", "/config/metadata/splunk", timeout=30
    )


@patch("tools.metadata_tools.sc4s_request")
def test_set_splunk_metadata(mock_sc4s_request):
    entries = [{"key": "juniper_netscreen", "metadata": "index", "value": "ns_index"}]
    set_splunk_metadata(entries)

    mock_sc4s_request.assert_called_once_with(
        "post", "/config/metadata/splunk", json={"entries": entries}, timeout=30
    )


@patch("tools.metadata_tools.sc4s_request")
def test_delete_splunk_metadata(mock_sc4s_request):
    delete_splunk_metadata()

    mock_sc4s_request.assert_called_once_with(
        "delete", "/config/metadata/splunk", timeout=30
    )


@patch("tools.metadata_tools.sc4s_request")
def test_get_compliance_overrides(mock_sc4s_request):
    get_compliance_overrides()

    mock_sc4s_request.assert_called_once_with(
        "get", "/config/metadata/compliance", timeout=10
    )


@patch("tools.metadata_tools.sc4s_request")
def test_set_compliance_override(mock_sc4s_request):
    conf = 'filter f_pci_zone { host("pci-*" type(glob)) };'
    csv = [
        {"filter_name": "f_pci_zone", "field_name": ".splunk.index", "value": "pci_idx"}
    ]
    set_compliance_override(conf, csv)

    mock_sc4s_request.assert_called_once_with(
        "post",
        "/config/metadata/compliance",
        json={"conf_content": conf, "csv_content": csv},
        timeout=30,
    )


@patch("tools.metadata_tools.sc4s_request")
def test_delete_compliance_override(mock_sc4s_request):
    delete_compliance_override()

    mock_sc4s_request.assert_called_once_with(
        "delete", "/config/metadata/compliance", timeout=30
    )
