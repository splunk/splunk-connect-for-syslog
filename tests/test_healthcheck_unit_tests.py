from unittest.mock import patch
import os
import pytest

from package.sbin.healthcheck import (
    app,
    str_to_bool,
    check_syslog_ng_health,
    subprocess,
    check_queue_size,
    get_list_of_destinations,
)

# str_to_bool
@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("t", True),
        ("y", True),
        ("yes", True),
        (" false ", False),
        ("0", False),
        ("f", False),
        ("n", False),
        ("no", False),
        ("random", False),
        ("", False),
    ],
)
def test_str_to_bool(input_val, expected):
    assert str_to_bool(input_val) == expected

# check_syslog_ng_health
@patch("subprocess.run")
def test_check_syslog_ng_health_success(mock_run):
    mock_run.return_value.returncode = 0
    assert check_syslog_ng_health() is True

@patch("subprocess.run")
def test_check_syslog_ng_health_failure(mock_run):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "some error"
    assert check_syslog_ng_health() is False

@patch("subprocess.run", side_effect=Exception("some exception"))
def test_check_syslog_ng_health_exception(mock_run):
    assert check_syslog_ng_health() is False

# check_queue_size
def test_check_queue_size_no_url():
    """
    If sc4s_dest_splunk_hec_destinations is not set, check_queue_size should fail.
    """
    assert check_queue_size(sc4s_dest_splunk_hec_destinations=None, max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_stats_fail(mock_run):
    """
    If syslog-ng-ctl stats command fails (returncode != 0), check_queue_size should fail.
    """
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "stats error"
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088"}, max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_no_matching_stats(mock_run):
    """
    If stats run successfully but do not contain the queued stat for the configured URL, it should fail.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "some;other;stat;line\nanother;stat"
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088"}, max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_exceeds_limit(mock_run):
    """
    If queue size from stats is > HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should fail.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;2000\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088"}, max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_under_limit(mock_run):
    """
    If queue size from stats is <= HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should pass.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;500\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088"}, max_queue_size=1000) is True

@patch("subprocess.run")
def test_check_queue_size_equals_limit(mock_run):
    """
    If queue size from stats is <= HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should pass.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;1000\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088"}, max_queue_size=1000) is True

@patch("subprocess.run")
def test_check_queue_size_multiple_destinations(mock_run):
    """
    If queue size for all destinations is <= HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should pass.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;300\n"
        "destination;queued;http://another.com:8088;500\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088", "http://another.com:8088"},
                            max_queue_size=1000) is True

@patch("subprocess.run")
def test_check_queue_size_multiple_destinations_over_limit(mock_run):
    """
    If queue size for at least one destination is > HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should fail.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;1300\n"
        "destination;queued;http://another.com:8088;500\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088", "http://another.com:8088"},
                            max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_multiple_destinations_all_over_limit(mock_run):
    """
    If queue size for all destinations is > HEALTHCHECK_MAX_QUEUE_SIZE, check_queue_size should fail.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;1300\n"
        "destination;queued;http://another.com:8088;1500\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088", "http://another.com:8088"},
                            max_queue_size=1000) is False

@patch("subprocess.run")
def test_check_queue_size_multiple_incomplete_info(mock_run):
    """
    If stats run successfully but do not contain stats for one of the desired destinations, it should fail.
    """
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = (
        "destination;queued;http://example.com:8088;300\n"
        "another;queued;http://other-url.com;1234"
    )
    assert check_queue_size(sc4s_dest_splunk_hec_destinations={"http://example.com:8088", "http://another.com:8088"},
                            max_queue_size=1000) is False

@patch("subprocess.run", side_effect=Exception("some exception"))
def test_check_queue_size_exception(mock_run):
    assert check_queue_size() is False

# /health endpoint
@pytest.fixture
def client():
    """
    Pytest fixture that provides a test client for the Flask application.
    """
    with app.test_client() as client:
        yield client

@patch.dict(
    os.environ,
    {
        "HEALTHCHECK_CHECK_QUEUE_SIZE": "false",
    },
    clear=True
)
@patch("subprocess.run")
def test_health_endpoint_no_queue_check(mock_run, client):
    """
    When CHECK_QUEUE_SIZE is false, only syslog-ng health is checked.
    """
    mock_run.return_value.returncode = 0

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

@patch.dict(
    os.environ,
    {
        "SC4S_DEST_SPLUNK_HEC_DEFAULT_URL": "http://my_test_url:1234",
        "SC4S_DEST_SPLUNK_HEC_OTHER_URL": "http://my_hec:1234",
        "SOME_OTHER_URL": "http://my_url/test_url",
        "SOME_OTHER_ENV_VARIABLE": "my_variable",
        "SC4S_LISTEN_STATUS_PORT": "1234",
    },
    clear=True
)
def test_get_destinations():
    """
    Check if get_list_of_destinations method parses and returns the expected
    destinations from environment variables.
    """
    destinations = get_list_of_destinations()

    assert len(destinations) == 2
    assert "http://my_test_url:1234" in destinations
    assert "http://my_hec:1234" in destinations
