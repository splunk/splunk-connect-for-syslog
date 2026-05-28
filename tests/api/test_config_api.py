import importlib
import os
from io import BytesIO
from unittest.mock import patch
import pytest


@pytest.fixture
def ctx_dir(tmp_path):
    """Patch file paths to use a temp directory."""
    parsers_dir = tmp_path / "parsers"
    parsers_dir.mkdir()
    with (
        patch("config_api.ENV_FILE", tmp_path / "env_file"),
        patch("config_api.PARSERS_DIR", parsers_dir),
    ):
        yield tmp_path


@pytest.fixture
def client(ctx_dir):
    os.environ["SC4S_API_MANAGEMENT_ENABLED"] = "true"
    import api

    importlib.reload(api)
    with api.app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# GET /config/env
# ---------------------------------------------------------------------------


def test_get_env(client, ctx_dir):
    env_file = ctx_dir / "env_file"
    env_file.write_text("SC4S_VAR=hello\nOTHER=world\n")

    resp = client.get("/config/env")

    assert resp.status_code == 200
    data = resp.get_json()
    assert "SC4S_VAR=hello" in data["content"]
    assert "OTHER=world" in data["content"]


def test_get_env_not_found(client):
    resp = client.get("/config/env")

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# POST /config/env
# ---------------------------------------------------------------------------


@patch("config_api.apply_with_rollback")
def test_set_env(mock_apply, client, ctx_dir):
    env_file = ctx_dir / "env_file"
    env_file.write_text("OLD=value\n")

    resp = client.post(
        "/config/env",
        data={"file": (BytesIO(b"NEW=value\n"), "env_file")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert "updated successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


def test_set_env_no_file(client):
    resp = client.post("/config/env")

    assert resp.status_code == 400
    assert "no file" in resp.get_json()["message"]


@patch("config_api.apply_with_rollback", side_effect=RuntimeError("restart failed"))
def test_set_env_rollback_on_failure(mock_apply, client, ctx_dir):
    env_file = ctx_dir / "env_file"
    env_file.write_text("ORIGINAL=value\n")

    resp = client.post(
        "/config/env",
        data={"file": (BytesIO(b"BAD=content\n"), "env_file")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 500
    assert "restart failed" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# POST /config/parser
# ---------------------------------------------------------------------------


@patch("config_api.apply_with_rollback")
def test_add_parser(mock_apply, client, ctx_dir):
    resp = client.post(
        "/config/parser",
        data={"file": (BytesIO(b"block parser test {}"), "test.conf")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert "parser added successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


def test_add_parser_no_file(client):
    resp = client.post("/config/parser")

    assert resp.status_code == 400
    assert "no file" in resp.get_json()["message"]


def test_add_parser_not_conf(client):
    resp = client.post(
        "/config/parser",
        data={"file": (BytesIO(b"content"), "test.txt")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    assert ".conf" in resp.get_json()["message"]


@patch("config_api.apply_with_rollback", side_effect=RuntimeError("syntax error"))
def test_add_parser_rollback_on_syntax_fail(mock_apply, client, ctx_dir):
    resp = client.post(
        "/config/parser",
        data={"file": (BytesIO(b"bad content"), "bad.conf")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 500
    assert "syntax error" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# GET /config/parser/<name>
# ---------------------------------------------------------------------------


def test_get_parser(client, ctx_dir):
    parser_file = ctx_dir / "parsers" / "my_parser.conf"
    parser_file.write_text("block parser my_parser {}")

    resp = client.get("/config/parser/my_parser.conf")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "my_parser.conf"
    assert "block parser" in data["content"]


def test_get_parser_auto_suffix(client, ctx_dir):
    parser_file = ctx_dir / "parsers" / "my_parser.conf"
    parser_file.write_text("content")

    resp = client.get("/config/parser/my_parser")

    assert resp.status_code == 200
    assert resp.get_json()["name"] == "my_parser.conf"


def test_get_parser_not_found(client):
    resp = client.get("/config/parser/nonexistent")

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# DELETE /config/parser/<name>
# ---------------------------------------------------------------------------


@patch("config_api.apply_with_rollback")
def test_delete_parser(mock_apply, client, ctx_dir):
    parser_file = ctx_dir / "parsers" / "my_parser.conf"
    parser_file.write_text("block parser my_parser {}")

    resp = client.delete("/config/parser/my_parser.conf")

    assert resp.status_code == 200
    assert "deleted successfully" in resp.get_json()["status"]
    mock_apply.assert_called_once()


def test_delete_parser_not_found(client):
    resp = client.delete("/config/parser/nonexistent")

    assert resp.status_code == 404
    assert "not found" in resp.get_json()["message"]


@patch("config_api.apply_with_rollback", side_effect=RuntimeError("syntax error"))
def test_delete_parser_rollback_on_failure(mock_apply, client, ctx_dir):
    parser_file = ctx_dir / "parsers" / "my_parser.conf"
    parser_file.write_text("block parser my_parser {}")

    resp = client.delete("/config/parser/my_parser.conf")

    assert resp.status_code == 500
    assert "syntax error" in resp.get_json()["message"]


# ---------------------------------------------------------------------------
# GET /config/parsers
# ---------------------------------------------------------------------------


def test_list_parsers(client, ctx_dir):
    (ctx_dir / "parsers" / "one.conf").write_text("p1")
    (ctx_dir / "parsers" / "two.conf").write_text("p2")
    (ctx_dir / "parsers" / "readme.txt").write_text("not a parser")

    resp = client.get("/config/parsers")

    assert resp.status_code == 200
    parsers = resp.get_json()["parsers"]
    assert sorted(parsers) == ["one.conf", "two.conf"]


def test_list_parsers_empty(client):
    resp = client.get("/config/parsers")

    assert resp.status_code == 200
    assert resp.get_json()["parsers"] == []
