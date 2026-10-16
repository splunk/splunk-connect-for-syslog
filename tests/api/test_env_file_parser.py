import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from env_file_parser import read_env_file
import utils

HELPER = Path(utils.__file__).with_name("env_file_parser.py")


def run_loader(path, keys, prelude=""):
    """Run the actual replacement for sourcing, without starting SC4S."""
    entrypoint = HELPER.with_name("entrypoint.sh").read_text()
    start = entrypoint.index("    _sc4s_env_values=$(python3")
    end = entrypoint.index("\n    apply_sc4s_defaults", start)
    block = (
        entrypoint[start:end]
        .replace("/opt/sc4s/env_file", str(path))
        .replace("/env_file_parser.py", str(HELPER))
    )
    script = path.parent / "load.sh"
    script.write_text(
        prelude + "\n" + block + '\nexec "$1" -c '
        "'import json, os, sys; print(json.dumps({k: os.environ.get(k) for k in sys.argv[1:]}))' "
        '"${@:2}"\n'
    )
    result = subprocess.run(
        ["bash", str(script), sys.executable, *keys],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


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
    with pytest.raises(subprocess.CalledProcessError) as error:
        run_loader(path, ["VALID"])
    assert error.value.returncode == 1
    assert error.value.stdout == ""
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


def test_invalid_utf8_does_not_disclose_values(tmp_path):
    path = tmp_path / "env_file"
    path.write_bytes(b"KEY=test-secret-value\xff")
    with pytest.raises(ValueError, match="expected UTF-8") as error:
        read_env_file(path)
    assert "test-secret-value" not in str(error.value)


def test_export_does_not_evaluate_bash_integer_values(tmp_path):
    marker = tmp_path / "executed"
    literal = f"x[$(touch {marker})]"
    path = tmp_path / "env_file"
    path.write_text(f"SC4S_TEST_INTEGER={literal}\n")
    assert run_loader(
        path, ["SC4S_TEST_INTEGER"], "declare -i SC4S_TEST_INTEGER=1"
    ) == {"SC4S_TEST_INTEGER": literal}
    assert not marker.exists()
