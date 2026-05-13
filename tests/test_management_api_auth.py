"""Unit tests for package/sbin/auth.py (management API bearer-token auth)."""

import pytest

from auth import (
    AUTH_TOKEN_ENV,
    AUTH_TOKEN_FILE_ENV,
    Sc4sTokenVerifier,
    build_token_verify,
    _load_token,
)


# ---------------------------------------------------------------------------
# _load_token() - file and env-var paths
# ---------------------------------------------------------------------------


def test_load_token_reads_from_env(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    monkeypatch.setenv(AUTH_TOKEN_ENV, "env-token")
    assert _load_token() == "env-token"


def test_load_token_returns_empty_when_both_unset(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    assert _load_token() == ""


def test_load_token_reads_from_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token\n")
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, str(token_file))
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    assert _load_token() == "file-token"


def test_load_token_file_takes_precedence_over_env(monkeypatch, tmp_path):
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token")
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, str(token_file))
    monkeypatch.setenv(AUTH_TOKEN_ENV, "env-token")
    assert _load_token() == "file-token"


def test_load_token_raises_runtime_error_for_missing_file(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, "/nonexistent/path/token.txt")
    with pytest.raises(RuntimeError, match=AUTH_TOKEN_FILE_ENV):
        _load_token()


def test_load_token_strips_trailing_newline_from_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token.txt"
    token_file.write_text("  my-token  \n")
    monkeypatch.setenv(AUTH_TOKEN_FILE_ENV, str(token_file))
    assert _load_token() == "my-token"


# ---------------------------------------------------------------------------
# build_token_verify() - opt-in via env var
# ---------------------------------------------------------------------------


def test_build_token_verify_returns_none_when_unset(monkeypatch):
    monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    assert build_token_verify() is None


def test_build_token_verify_returns_none_when_empty(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_ENV, "")
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    assert build_token_verify() is None


def test_build_token_verify_returns_verifier_when_set(monkeypatch):
    monkeypatch.setenv(AUTH_TOKEN_ENV, "s3cret")
    monkeypatch.delenv(AUTH_TOKEN_FILE_ENV, raising=False)
    assert isinstance(build_token_verify(), Sc4sTokenVerifier)


# ---------------------------------------------------------------------------
# Sc4sTokenVerifier.verify_token
# ---------------------------------------------------------------------------


def test_verify_token_accepts_matching_token():
    verifier = Sc4sTokenVerifier("correct-token")
    assert verifier.verify_token("correct-token") is True


def test_verify_token_rejects_wrong_token():
    verifier = Sc4sTokenVerifier("correct-token")
    assert verifier.verify_token("wrong-token") is False


def test_verify_token_rejects_empty_string():
    verifier = Sc4sTokenVerifier("correct-token")
    assert verifier.verify_token("") is False


def test_verify_token_is_case_sensitive():
    verifier = Sc4sTokenVerifier("CaseSensitive")
    assert verifier.verify_token("casesensitive") is False
    assert verifier.verify_token("CaseSensitive") is True
