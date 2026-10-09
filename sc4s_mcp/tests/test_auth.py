import asyncio

import pytest

from auth import (
    AUTH_TOKEN_ENV,
    AUTH_TOKEN_FILE_ENV,
    StaticBearerTokenVerifier,
    build_auth_provider,
)
from fastmcp.server.auth import AccessToken
from utils.token_utils import load_token


def _verify(verifier: StaticBearerTokenVerifier, token: str):
    """Run the async verifier synchronously to avoid a pytest-asyncio dep."""
    return asyncio.run(verifier.verify_token(token))


# ---------------------------------------------------------------------------
# build_auth_provider() - opt-in via env var
# ---------------------------------------------------------------------------


def test_build_auth_provider_returns_none_when_env_unset(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    assert build_auth_provider() is None


def test_build_auth_provider_returns_none_when_env_empty(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_ENV, "")
    assert build_auth_provider() is None


def test_build_auth_provider_returns_none_when_env_whitespace(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_ENV, "   \t\n")
    assert build_auth_provider() is None


def test_build_auth_provider_returns_verifier_when_env_set(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_ENV, "s3cret-token")
    provider = build_auth_provider()
    assert isinstance(provider, StaticBearerTokenVerifier)


# ---------------------------------------------------------------------------
# StaticBearerTokenVerifier.__init__ - input validation
# ---------------------------------------------------------------------------


def test_verifier_rejects_empty_expected_token():
    with pytest.raises(ValueError):
        StaticBearerTokenVerifier("")


def test_verifier_rejects_whitespace_expected_token():
    with pytest.raises(ValueError):
        StaticBearerTokenVerifier("   ")


# ---------------------------------------------------------------------------
# StaticBearerTokenVerifier.verify_token - happy path
# ---------------------------------------------------------------------------


def test_verify_token_accepts_matching_token():
    verifier = StaticBearerTokenVerifier("correct-horse-battery-staple")
    result = _verify(verifier, "correct-horse-battery-staple")

    assert isinstance(result, AccessToken)
    assert result.token == "correct-horse-battery-staple"
    assert result.client_id == "sc4s-mcp-client"
    assert result.scopes == []
    assert result.expires_at is None


# ---------------------------------------------------------------------------
# StaticBearerTokenVerifier.verify_token - rejection cases
# ---------------------------------------------------------------------------


def test_verify_token_rejects_empty_string():
    verifier = StaticBearerTokenVerifier("expected")
    assert _verify(verifier, "") is None


def test_verify_token_rejects_whitespace_only():
    verifier = StaticBearerTokenVerifier("expected")
    assert _verify(verifier, "   ") is None


def test_verify_token_rejects_wrong_token():
    verifier = StaticBearerTokenVerifier("expected")
    assert _verify(verifier, "wrong") is None


def test_verify_token_rejects_token_with_different_length():
    verifier = StaticBearerTokenVerifier("expected-32-bytes-or-thereabouts")

    assert _verify(verifier, "x") is None
    assert _verify(verifier, "x" * 1024) is None


def test_verify_token_is_case_sensitive():
    verifier = StaticBearerTokenVerifier("CaseSensitive")
    assert _verify(verifier, "casesensitive") is None
    assert _verify(verifier, "CaseSensitive") is not None


# ---------------------------------------------------------------------------
# load_token() - file and env-var paths
# ---------------------------------------------------------------------------


def test_load_token_reads_from_env(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    monkeypatch.setenv(AUTH_TOKEN_ENV, "env-token")
    assert load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV) == "env-token"


def test_load_token_returns_empty_when_both_unset(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    assert load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV) == ""


def test_load_token_reads_from_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token\n")
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, str(token_file))
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    assert load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV) == "file-token"


def test_load_token_file_takes_precedence_over_env(monkeypatch, tmp_path):
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token")
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, str(token_file))
    monkeypatch.setenv(AUTH_TOKEN_ENV, "env-token")
    assert load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV) == "file-token"


def test_load_token_raises_runtime_error_for_missing_file(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, "/nonexistent/path/token.txt")
    with pytest.raises(RuntimeError, match=AUTH_TOKEN_FILE_ENV):
        load_token(AUTH_TOKEN_ENV, AUTH_TOKEN_FILE_ENV)
