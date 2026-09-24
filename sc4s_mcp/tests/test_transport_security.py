import pytest
from fastapi.testclient import TestClient

from server import _build_api


def _client(monkeypatch, *, allowed_hosts=None, allowed_origins=None):
    if allowed_hosts is None:
        monkeypatch.delenv("SC4S_MCP_ALLOWED_HOSTS", raising=False)
    else:
        monkeypatch.setenv("SC4S_MCP_ALLOWED_HOSTS", allowed_hosts)

    if allowed_origins is None:
        monkeypatch.delenv("SC4S_MCP_ALLOWED_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("SC4S_MCP_ALLOWED_ORIGINS", allowed_origins)

    return TestClient(_build_api())


@pytest.mark.parametrize(
    "host", ["localhost:8000", "127.0.0.1:8000", "[::1]:8000"]
)
def test_default_host_allowlist_accepts_loopback_hosts(monkeypatch, host):
    with _client(monkeypatch) as client:
        response = client.get("/health", headers={"Host": host})

    assert response.status_code == 200


def test_default_host_allowlist_rejects_non_loopback_hosts(monkeypatch):
    with _client(monkeypatch) as client:
        response = client.get("/health", headers={"Host": "evil.example"})

    assert response.status_code == 421


def test_configured_host_allowlist_accepts_remote_host(monkeypatch):
    with _client(monkeypatch, allowed_hosts="mcp.example.com") as client:
        assert (
            client.get("/health", headers={"Host": "mcp.example.com:8000"}).status_code
            == 200
        )
        assert (
            client.get("/health", headers={"Host": "other.example.com"}).status_code
            == 421
        )


def test_configured_host_port_does_not_allow_other_ports(monkeypatch):
    with _client(monkeypatch, allowed_hosts="mcp.example.com:8443") as client:
        assert (
            client.get("/health", headers={"Host": "mcp.example.com:8443"}).status_code
            == 200
        )
        assert (
            client.get("/health", headers={"Host": "mcp.example.com:8000"}).status_code
            == 421
        )


def test_origin_is_rejected_unless_explicitly_allowed(monkeypatch):
    with _client(monkeypatch) as client:
        assert client.get("/health", headers={"Host": "localhost:8000"}).status_code == 200
        assert client.get(
            "/health",
            headers={"Host": "localhost:8000", "Origin": "https://evil.example"},
        ).status_code == 403

    with _client(
        monkeypatch,
        allowed_origins="https://inspector.example.com",
    ) as client:
        assert client.get(
            "/health",
            headers={
                "Host": "localhost:8000",
                "Origin": "https://inspector.example.com",
            },
        ).status_code == 200


def test_mcp_initialization_rejects_untrusted_origin(monkeypatch):
    with _client(monkeypatch) as client:
        response = client.post(
            "/mcp/",
            headers={
                "Host": "localhost:8000",
                "Origin": "https://evil.example",
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "security-test", "version": "1.0"},
                },
            },
        )

    assert response.status_code == 403


def test_origin_allowlist_uses_exact_scheme_host_and_port(monkeypatch):
    with _client(
        monkeypatch,
        allowed_origins="https://inspector.example.com:8443",
    ) as client:
        assert client.get(
            "/health",
            headers={
                "Host": "localhost:8000",
                "Origin": "https://inspector.example.com:8443",
            },
        ).status_code == 200
        assert client.get(
            "/health",
            headers={
                "Host": "localhost:8000",
                "Origin": "http://inspector.example.com:8443",
            },
        ).status_code == 403
        assert client.get(
            "/health",
            headers={
                "Host": "localhost:8000",
                "Origin": "https://inspector.example.com",
            },
        ).status_code == 403
