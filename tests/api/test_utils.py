import subprocess
from unittest.mock import call, patch

import pytest

from utils import apply_with_rollback, restart_syslog_ng


def completed(args, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args, returncode, stdout, stderr)


@patch("utils.time.sleep")
@patch("utils.time.monotonic", side_effect=[0, 0, 0.5, 0.5, 0.5])
@patch("utils.subprocess.run")
def test_restart_waits_for_healthy_replacement(mock_run, _clock, mock_sleep):
    mock_run.side_effect = [
        completed(["pgrep"], stdout="101\n"),
        completed(["pkill"]),
        completed(["pgrep"], stdout="101\n"),
        completed(["pgrep"], stdout="202\n"),
        completed(["syslog-ng-ctl"]),
    ]

    restart_syslog_ng()

    assert mock_run.call_args_list == [
        call(
            ["pgrep", "-x", "syslog-ng"],
            capture_output=True,
            text=True,
            timeout=1,
        ),
        call(
            ["pkill", "syslog-ng"],
            capture_output=True,
            text=True,
            timeout=10,
        ),
        call(
            ["pgrep", "-x", "syslog-ng"],
            capture_output=True,
            text=True,
            timeout=1,
        ),
        call(
            ["pgrep", "-x", "syslog-ng"],
            capture_output=True,
            text=True,
            timeout=1,
        ),
        call(
            ["syslog-ng-ctl", "healthcheck", "--timeout", "1"],
            capture_output=True,
            text=True,
            timeout=2,
        ),
    ]
    mock_sleep.assert_called_once_with(0.5)


@patch("utils.time.sleep")
@patch("utils.time.monotonic", side_effect=[0, 0, 30])
@patch("utils.subprocess.run")
def test_restart_times_out_when_new_process_never_appears(
    mock_run, _mock_monotonic, mock_sleep
):
    mock_run.side_effect = [
        completed(["pgrep"], stdout="101\n"),
        completed(["pkill"]),
        completed(["pgrep"], returncode=1),
    ]

    with pytest.raises(RuntimeError, match="timed out after 30 seconds"):
        restart_syslog_ng()

    mock_sleep.assert_not_called()


@patch("utils.time.sleep")
@patch("utils.time.monotonic", side_effect=[0, 0, 30])
@patch("utils.subprocess.run")
def test_restart_times_out_when_new_process_is_unhealthy(
    mock_run, _mock_monotonic, mock_sleep
):
    mock_run.side_effect = [
        completed(["pgrep"], stdout="101\n"),
        completed(["pkill"]),
        completed(["pgrep"], stdout="202\n"),
        completed(["syslog-ng-ctl"], returncode=1, stderr="not ready"),
    ]

    with pytest.raises(RuntimeError, match="timed out after 30 seconds"):
        restart_syslog_ng()

    mock_sleep.assert_not_called()


@patch("utils.time.sleep")
@patch("utils.time.monotonic", side_effect=[0, 0, 30])
@patch("utils.subprocess.run")
def test_restart_rejects_healthy_process_after_deadline(
    mock_run, _mock_monotonic, mock_sleep
):
    mock_run.side_effect = [
        completed(["pgrep"], stdout="101\n"),
        completed(["pkill"]),
        completed(["pgrep"], stdout="202\n"),
        completed(["syslog-ng-ctl"]),
    ]

    with pytest.raises(RuntimeError, match="timed out after 30 seconds"):
        restart_syslog_ng()

    mock_sleep.assert_not_called()


@patch("utils.subprocess.run")
def test_restart_fails_immediately_when_kill_fails(mock_run):
    mock_run.side_effect = [
        completed(["pgrep"], stdout="101\n"),
        completed(["pkill"], returncode=1, stderr="no process"),
    ]

    message = "syslog-ng restart failed: no process"
    with pytest.raises(RuntimeError, match=message):
        restart_syslog_ng()


def test_apply_restart_failure_restores_files_and_restarts_runtime(tmp_path):
    existing = tmp_path / "existing.conf"
    existing.write_text("old\n", encoding="utf-8")
    created = tmp_path / "created.conf"

    with (
        patch("utils.syntax_check"),
        patch(
            "utils.restart_syslog_ng",
            side_effect=[RuntimeError("restart timed out"), None],
        ) as mock_restart,
        pytest.raises(RuntimeError, match="restart timed out"),
    ):
        apply_with_rollback(
            {
                existing: "new\n",
                created: "created\n",
            }
        )

    assert existing.read_text(encoding="utf-8") == "old\n"
    assert not created.exists()
    assert not existing.with_suffix(".conf.backup").exists()
    assert not created.with_suffix(".conf.backup").exists()
    assert mock_restart.call_count == 2


def test_apply_reports_original_and_runtime_rollback_failures(tmp_path):
    config = tmp_path / "parser.conf"
    config.write_text("old\n", encoding="utf-8")

    with (
        patch("utils.syntax_check"),
        patch(
            "utils.restart_syslog_ng",
            side_effect=[
                RuntimeError("apply restart timed out"),
                RuntimeError("rollback restart timed out"),
            ],
        ),
        pytest.raises(RuntimeError) as exc_info,
    ):
        apply_with_rollback({config: "new\n"})

    assert config.read_text(encoding="utf-8") == "old\n"
    assert str(exc_info.value) == (
        "configuration apply failed: apply restart timed out; "
        "rollback failed: rollback restart timed out"
    )


def test_syntax_failure_restores_files_without_restarting_runtime(tmp_path):
    config = tmp_path / "parser.conf"
    config.write_text("old\n", encoding="utf-8")

    with (
        patch("utils.syntax_check", side_effect=RuntimeError("syntax error")),
        patch("utils.restart_syslog_ng") as mock_restart,
        pytest.raises(RuntimeError, match="syntax error"),
    ):
        apply_with_rollback({config: "invalid\n"})

    assert config.read_text(encoding="utf-8") == "old\n"
    assert not config.with_suffix(".conf.backup").exists()
    mock_restart.assert_not_called()


def test_apply_reports_original_and_file_restore_failures(tmp_path):
    config = tmp_path / "parser.conf"
    config.write_text("old\n", encoding="utf-8")

    with (
        patch("utils.syntax_check"),
        patch(
            "utils.restart_syslog_ng",
            side_effect=RuntimeError("apply restart timed out"),
        ) as mock_restart,
        patch("utils.rollback", side_effect=OSError("restore denied")),
        pytest.raises(RuntimeError) as exc_info,
    ):
        apply_with_rollback({config: "new\n"})

    assert str(exc_info.value) == (
        "configuration apply failed: apply restart timed out; "
        "rollback failed: restore denied"
    )
    mock_restart.assert_called_once_with()


def test_successful_apply_keeps_new_files_and_restarts_once(tmp_path):
    config = tmp_path / "parser.conf"
    config.write_text("old\n", encoding="utf-8")

    with (
        patch("utils.syntax_check") as mock_syntax_check,
        patch("utils.restart_syslog_ng") as mock_restart,
    ):
        apply_with_rollback({config: "new\n"})

    assert config.read_text(encoding="utf-8") == "new\n"
    assert not config.with_suffix(".conf.backup").exists()
    mock_syntax_check.assert_called_once_with()
    mock_restart.assert_called_once_with()
