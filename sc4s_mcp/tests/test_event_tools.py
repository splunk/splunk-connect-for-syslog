"""Tests for MCP raw-text syslog sending."""

from unittest.mock import Mock

import pytest

from utils import syslog_sender


def test_send_text_sends_non_empty_lines_over_udp(monkeypatch):
    sock = Mock()
    sock.sendto.side_effect = lambda payload, _destination: len(payload)
    monkeypatch.setattr(syslog_sender.socket, "socket", Mock(return_value=sock))
    monkeypatch.setenv("SC4S_API_URL", "http://sc4s.example:8080")

    result = syslog_sender.send_text(
        text="<14>one\n\n<14>two",
        protocol="udp",
        port=514,
        timeout=5,
    )

    assert result["sent"] == 2
    assert result["bytes_sent"] == len(b"<14>one") + len(b"<14>two")
    assert [call.args for call in sock.sendto.call_args_list] == [
        (b"<14>one", ("sc4s.example", 514)),
        (b"<14>two", ("sc4s.example", 514)),
    ]


def test_send_text_rejects_an_empty_request(monkeypatch):
    monkeypatch.setenv("SC4S_API_URL", "http://sc4s.example:8080")

    with pytest.raises(ValueError, match="No syslog events"):
        syslog_sender.send_text(
            text="\n\t", protocol="udp", port=514, timeout=5
        )


def test_text_tool_maps_invalid_input(monkeypatch):
    from tools import event_tools

    def raise_input_error(**_kwargs):
        raise ValueError("No syslog events found in raw text input")

    monkeypatch.setattr(event_tools, "send_text", raise_input_error)

    assert event_tools.send_syslog_text("") == {
        "status": "error",
        "error": "invalid_request",
        "message": "No syslog events found in raw text input",
    }
