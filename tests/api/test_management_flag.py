import importlib
import os
from unittest.mock import patch
import pytest


def _make_client(enabled: bool):
    if enabled:
        os.environ["SC4S_API_MANAGEMENT_ENABLED"] = "true"
    else:
        os.environ.pop("SC4S_API_MANAGEMENT_ENABLED", None)
    import api
    importlib.reload(api)
    return api.app.test_client()


@pytest.fixture(autouse=True)
def _restore_env():
    yield
    os.environ.pop("SC4S_API_MANAGEMENT_ENABLED", None)


@patch("healthcheck.check_syslog_ng_health", return_value=True)
def test_health_always_reachable_when_disabled(_mock_health):
    client = _make_client(enabled=False)
    assert client.get("/health").status_code == 200


@patch("healthcheck.check_syslog_ng_health", return_value=True)
def test_health_always_reachable_when_enabled(_mock_health):
    client = _make_client(enabled=True)
    assert client.get("/health").status_code == 200


def test_config_env_disabled_returns_404():
    client = _make_client(enabled=False)
    assert client.get("/config/env").status_code == 404


def test_metadata_splunk_disabled_returns_404():
    client = _make_client(enabled=False)
    assert client.get("/config/metadata/splunk").status_code == 404


def test_management_routes_registered_when_enabled():
    import api
    _make_client(enabled=True)
    importlib.reload(api)
    rules = {r.rule for r in api.app.url_map.iter_rules()}
    assert "/config/env" in rules
    assert "/config/parsers" in rules
    assert "/config/metadata/splunk" in rules


def test_management_routes_absent_when_disabled():
    import api
    _make_client(enabled=False)
    importlib.reload(api)
    rules = {r.rule for r in api.app.url_map.iter_rules()}
    assert "/config/env" not in rules
    assert "/config/parsers" not in rules
    assert "/config/metadata/splunk" not in rules
