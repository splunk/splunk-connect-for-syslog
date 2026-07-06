import subprocess
from unittest.mock import call, patch

import pytest

from utils import restart_syslog_ng


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
