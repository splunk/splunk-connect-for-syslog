import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from env_file_parser import read_env_file
import utils

HELPER = Path(utils.__file__).with_name("env_file_parser.py")


def run_loader(path, keys, prelude="", initialize=True):
    """Run the actual replacement for sourcing, without starting SC4S."""
    entrypoint = HELPER.with_name("entrypoint.sh").read_text()
    initial = (
        entrypoint[
            entrypoint.index("# Save initial env_file keys") : entrypoint.index(
                "# Loop that runs and restarts syslog-ng"
            )
        ]
        if initialize
        else ""
    )
    start = entrypoint.index("  # Unset env variables that were removed")
    end = entrypoint.index("\n  refresh_source_sets", start)
    block = (
        (initial + entrypoint[start:end])
        .replace("/opt/sc4s/env_file", str(path))
        .replace("/env_file_parser.py", str(HELPER))
        .replace("/tmp/sc4s_", str(path.parent / "sc4s_"))
    )
    script = path.parent / "load.sh"
    script.write_text(
        prelude
        + "\napply_sc4s_defaults() { :; }\nnormalize_hec_url() { :; }\n"
        + block
        + '\nexec "$1" -c '
        "'import json, os, sys; print(json.dumps({k: os.environ.get(k) for k in sys.argv[1:]}))' "
        '"${@:2}"\n'
    )
    result = subprocess.run(
        ["bash", str(script), sys.executable, *keys],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout.splitlines()[-1])


def test_runtime_and_syntax_check_preserve_literal_values(tmp_path, monkeypatch):
    marker = tmp_path / "executed"
    values = {
        "SC4S_TEST_PASSWORD": "pa$$w0rd$HOME",
        "SC4S_TEST_QUOTED": '"quoted value"',
        "SC4S_TEST_COMMAND": f"x$(id>{marker})y",
        "SC4S_TEST_WORDS": "two words",
        "SC4S_TEST_PADDED": "  value # literal  ",
        "SC4S_TEST_EQUALS": "a=b=c",
        "SC4S_TEST_BACKSLASH": r"a\nb\\c",
        "SC4S_TEST_EMPTY": "",
    }
    path = tmp_path / "env_file"
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()))
    assert run_loader(path, values) == values
    assert not marker.exists()

    monkeypatch.setattr(utils, "ENV_FILE", path)
    run = Mock(return_value=subprocess.CompletedProcess([], 0, "", ""))
    monkeypatch.setattr(utils.subprocess, "run", run)
    utils.syntax_check()
    run.assert_called_once()
    checked = run.call_args.kwargs["env"]
    assert {key: checked[key] for key in values} == values


def test_comments_crlf_duplicates_and_tracking_keys(tmp_path):
    path = tmp_path / "env_file"
    path.write_bytes(
        "\ufeff # comment\r\n\r\n  Z=first\r\nA=value\r\nZ=last  ".encode()
    )
    assert read_env_file(path) == {
        "A": "value",
        "Z": "last  ",
    }
    result = subprocess.run(
        [sys.executable, str(HELPER), str(path), "--keys"],
        capture_output=True,
        check=True,
    )
    assert result.stdout == b"A\nZ\n"


@pytest.mark.parametrize(
    "invalid",
    [
        b"BAD-NAME=test-secret-value",
        b"=test-secret-value",
        b"KEY=test-secret-value\0",
        b"pid=test-secret-value",
        b"BASH_ENV=test-secret-value",
        b"_sc4s_env_values=test-secret-value",
        b"BARE_NAME",
        b"my.dotted.var=test-secret-value",
    ],
)
def test_invalid_file_emits_no_assignments_or_secrets(tmp_path, invalid, monkeypatch):
    path = tmp_path / "env_file"
    path.write_bytes(b"VALID=value\n" + invalid + b"\n")
    result = subprocess.run(
        [sys.executable, str(HELPER), str(path)], capture_output=True
    )
    assert result.returncode != 0
    assert result.stdout == b""
    assert b":2:" in result.stderr
    assert b"test-secret-value" not in result.stderr
    assert run_loader(path, ["VALID"]) == {"VALID": "value"}
    startup = subprocess.run(
        [sys.executable, str(HELPER), str(path), "--skip-invalid"],
        capture_output=True,
        check=True,
    )
    assert startup.stdout == b"VALID=value\n"
    assert b"Warning:" in startup.stderr
    assert b":2:" in startup.stderr
    assert b"test-secret-value" not in startup.stderr
    monkeypatch.setattr(utils, "ENV_FILE", path)
    run = Mock()
    monkeypatch.setattr(utils.subprocess, "run", run)
    with pytest.raises(ValueError, match="Invalid env_file"):
        utils.syntax_check()
    run.assert_not_called()


def test_empty_file_loads_without_assignments(tmp_path):
    path = tmp_path / "env_file"
    path.write_text("")
    assert run_loader(path, []) == {}


def test_bare_name_preserves_inherited_value_and_tracks_removals(tmp_path, monkeypatch):
    path = tmp_path / "env_file"
    path.write_text("SC4S_TEST_BARE\nSC4S_TEST_VALUE=two words\n")
    monkeypatch.setenv("SC4S_TEST_BARE", "inherited\nvalue")
    tracked = tmp_path / "sc4s_prev_env_keys"
    tracked.write_text("SC4S_TEST_BARE\nSC4S_TEST_REMOVED\n")
    assert run_loader(
        path,
        ["SC4S_TEST_BARE", "SC4S_TEST_VALUE", "SC4S_TEST_REMOVED"],
        "export SC4S_TEST_REMOVED=old",
        initialize=False,
    ) == {
        "SC4S_TEST_BARE": "inherited\nvalue",
        "SC4S_TEST_VALUE": "two words",
        "SC4S_TEST_REMOVED": None,
    }
    assert tracked.read_text() == "SC4S_TEST_BARE\nSC4S_TEST_VALUE\n"


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read mode-000 files")
@pytest.mark.parametrize("initialize", [True, False])
def test_unreadable_file_preserves_environment_and_tracking(tmp_path, initialize):
    path = tmp_path / "env_file"
    path.write_text("SC4S_TEST_KEEP=replacement\n")
    tracked = tmp_path / "sc4s_prev_env_keys"
    if not initialize:
        tracked.write_text("SC4S_TEST_KEEP\n")
    path.chmod(0)
    try:
        assert run_loader(
            path, ["SC4S_TEST_KEEP"], "export SC4S_TEST_KEEP=original", initialize
        ) == {"SC4S_TEST_KEEP": "original"}
    finally:
        path.chmod(0o600)
    assert tracked.read_text() == ("" if initialize else "SC4S_TEST_KEEP\n")


def test_invalid_utf8_does_not_disclose_values(tmp_path):
    path = tmp_path / "env_file"
    path.write_bytes(b"KEY=test-secret-value\xff")
    with pytest.raises(ValueError, match="expected UTF-8") as error:
        read_env_file(path)
    assert "test-secret-value" not in str(error.value)
    assert run_loader(path, ["SC4S_TEST_KEEP"], "export SC4S_TEST_KEEP=original") == {
        "SC4S_TEST_KEEP": "original"
    }


def test_readonly_variable_does_not_stop_loading_other_values(tmp_path):
    path = tmp_path / "env_file"
    path.write_text("SC4S_TEST_READONLY=new\nSC4S_TEST_VALUE=two words\n")
    assert run_loader(
        path,
        ["SC4S_TEST_READONLY", "SC4S_TEST_VALUE"],
        "export SC4S_TEST_READONLY=old\nreadonly SC4S_TEST_READONLY",
    ) == {"SC4S_TEST_READONLY": "old", "SC4S_TEST_VALUE": "two words"}


def test_export_does_not_evaluate_bash_integer_values(tmp_path):
    marker = tmp_path / "executed"
    literal = f"x[$(touch {marker})]"
    path = tmp_path / "env_file"
    path.write_text(f"SC4S_TEST_INTEGER={literal}\n")
    assert run_loader(
        path, ["SC4S_TEST_INTEGER"], "declare -i SC4S_TEST_INTEGER=1"
    ) == {"SC4S_TEST_INTEGER": literal}
    assert not marker.exists()
