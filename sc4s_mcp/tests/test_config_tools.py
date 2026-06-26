from unittest.mock import patch

from tools.configuration_tools import (
    get_parser_creation_guide,
    list_vendors,
    list_all_parsers,
    list_vendor_parsers,
    get_parser,
    search_docs,
    health,
    set_env,
    get_env,
    add_parser,
    delete_parser,
    list_custom_parsers,
    get_custom_parser,
)


# ---------------------------------------------------------------------------
# Local tools
# ---------------------------------------------------------------------------


@patch("tools.configuration_tools.SKILL_DIR")
def test_get_parser_creation_guide(mock_skill_dir, tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("# Parser Guide")
    refs_dir = tmp_path / "references"
    refs_dir.mkdir()
    (refs_dir / "testing-parsers.md").write_text("# Testing")

    mock_skill_dir.__truediv__ = lambda self, key: tmp_path / key
    mock_skill_dir.return_value = tmp_path

    with patch("tools.configuration_tools.SKILL_DIR", tmp_path):
        result = get_parser_creation_guide()

    assert "# Parser Guide" in result
    assert "# Testing" in result


@patch("tools.configuration_tools.SKILL_DIR")
def test_get_parser_creation_guide_not_found(mock_skill_dir, tmp_path):
    with patch("tools.configuration_tools.SKILL_DIR", tmp_path):
        result = get_parser_creation_guide()

    assert result == "Parser creation guide not found"


@patch("tools.configuration_tools.REPO_ROOT")
def test_list_vendors(mock_repo_root, tmp_path):
    vendor_dir = tmp_path / "docs" / "sources" / "vendor"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "cisco").mkdir()
    (vendor_dir / "juniper").mkdir()
    (vendor_dir / "some_file.txt").touch()

    mock_repo_root.__truediv__ = lambda self, key: tmp_path / key

    result = list_vendors()
    assert sorted(result) == ["cisco", "juniper"]


@patch("tools.configuration_tools.REPO_ROOT")
def test_list_all_parsers(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    (addons_dir / "cisco").mkdir(parents=True)
    (addons_dir / "cisco" / "cisco_asa.conf").write_text("parser")
    (addons_dir / "juniper").mkdir(parents=True)
    (addons_dir / "juniper" / "juniper_junos.conf").write_text("parser")

    mock_repo_root.__truediv__ = lambda self, key: tmp_path / key
    mock_repo_root.__eq__ = lambda self, other: tmp_path == other
    mock_repo_root.__hash__ = lambda self: hash(tmp_path)

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = list_all_parsers()

    assert len(result) == 2
    assert any("cisco_asa.conf" in r for r in result)
    assert any("juniper_junos.conf" in r for r in result)


@patch("tools.configuration_tools.REPO_ROOT")
def test_list_vendor_parsers(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    (addons_dir / "cisco").mkdir(parents=True)
    (addons_dir / "cisco" / "cisco_asa.conf").write_text(
        "# cisco_asa parser\nvendor: cisco"
    )
    (addons_dir / "juniper").mkdir(parents=True)
    (addons_dir / "juniper" / "juniper_junos.conf").write_text("# juniper parser")

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = list_vendor_parsers("cisco")

    assert len(result) == 1
    assert "cisco_asa.conf" in result[0]


@patch("tools.configuration_tools.REPO_ROOT")
def test_list_vendor_parsers_no_match(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    addons_dir.mkdir(parents=True)
    (addons_dir / "cisco_asa.conf").write_text("cisco parser")

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = list_vendor_parsers("paloalto")

    assert result == []


@patch("tools.configuration_tools.REPO_ROOT")
def test_get_parser_found(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    addons_dir.mkdir(parents=True)
    (addons_dir / "cisco_asa.conf").write_text("block parser cisco_asa {}")

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = get_parser("cisco_asa.conf")

    assert result["found"] is True
    assert "cisco_asa" in result["content"]


@patch("tools.configuration_tools.REPO_ROOT")
def test_get_parser_by_stem(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    addons_dir.mkdir(parents=True)
    (addons_dir / "cisco_asa.conf").write_text("block parser cisco_asa {}")

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = get_parser("cisco_asa")

    assert result["found"] is True


@patch("tools.configuration_tools.REPO_ROOT")
def test_get_parser_not_found(mock_repo_root, tmp_path):
    addons_dir = tmp_path / "package" / "shared" / "addons"
    addons_dir.mkdir(parents=True)

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = get_parser("nonexistent")

    assert result["found"] is False
    assert "not found" in result["message"]


@patch("tools.configuration_tools.REPO_ROOT")
def test_search_docs(mock_repo_root, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "getting_started.md").write_text(
        "Line 1\nSC4S listens on port 514\nLine 3"
    )

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = search_docs("port 514")

    assert len(result) == 1
    assert "port 514" in result[0]


@patch("tools.configuration_tools.REPO_ROOT")
def test_search_docs_no_match(mock_repo_root, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "readme.md").write_text("nothing here")

    with patch("tools.configuration_tools.REPO_ROOT", tmp_path):
        result = search_docs("nonexistent_pattern")

    assert result == []


def test_search_docs_invalid_regex():
    result = search_docs("[invalid")
    assert len(result) == 1
    assert "Invalid regex" in result[0]


# ---------------------------------------------------------------------------
# Remote/HTTP tools (mock sc4s_request)
# ---------------------------------------------------------------------------


@patch("tools.configuration_tools._sc4s_request")
def test_health(mock_req):
    health()
    mock_req.assert_called_once_with("get", "/health", timeout=10)


@patch("tools.configuration_tools._sc4s_request")
def test_get_env(mock_req):
    get_env()
    mock_req.assert_called_once_with("get", "/config/env", timeout=10)


@patch("tools.configuration_tools._sc4s_request")
def test_set_env(mock_req):
    set_env("SC4S_VAR=value\n")
    mock_req.assert_called_once_with(
        "post",
        "/config/env",
        files={"file": ("env_file", b"SC4S_VAR=value\n")},
        timeout=30,
    )


@patch("tools.configuration_tools._sc4s_request")
def test_add_parser(mock_req):
    add_parser("my_parser.conf", "block parser my_parser {}")
    mock_req.assert_called_once_with(
        "post",
        "/config/parser",
        files={"file": ("my_parser.conf", b"block parser my_parser {}")},
        timeout=30,
    )


@patch("tools.configuration_tools._sc4s_request")
def test_add_parser_auto_suffix(mock_req):
    add_parser("my_parser", "content")
    args = mock_req.call_args
    assert args[1]["files"]["file"][0] == "my_parser.conf"


@patch("tools.configuration_tools._sc4s_request")
def test_delete_parser(mock_req):
    delete_parser("my_parser")
    mock_req.assert_called_once_with("delete", "/config/parser/my_parser", timeout=30)


@patch("tools.configuration_tools._sc4s_request")
def test_list_custom_parsers(mock_req):
    list_custom_parsers()
    mock_req.assert_called_once_with("get", "/config/parsers", timeout=10)


@patch("tools.configuration_tools._sc4s_request")
def test_get_custom_parser(mock_req):
    get_custom_parser("my_parser")
    mock_req.assert_called_once_with("get", "/config/parser/my_parser", timeout=10)
