import pytest

from utils.transport import TransportMode, resolve_transport


@pytest.fixture(autouse=True)
def _isolate_transport_env(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)


def test_resolve_transport_defaults_to_stdio_when_unset():
    assert resolve_transport() == TransportMode.STDIO


def test_resolve_transport_returns_http_for_http(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    assert resolve_transport() == TransportMode.HTTP


def test_resolve_transport_returns_stdio_for_stdio(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "stdio")
    assert resolve_transport() == TransportMode.STDIO


def test_resolve_transport_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "HTTP")
    assert resolve_transport() == TransportMode.HTTP

    monkeypatch.setenv("MCP_TRANSPORT", "STDIO")
    assert resolve_transport() == TransportMode.STDIO


def test_resolve_transport_strips_whitespace(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "  http  ")
    assert resolve_transport() == TransportMode.HTTP


def test_resolve_transport_falls_back_to_stdio_for_unknown_value(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "htpp")
    assert resolve_transport() == TransportMode.STDIO


def test_resolve_transport_falls_back_to_stdio_for_empty_string(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "")
    assert resolve_transport() == TransportMode.STDIO
