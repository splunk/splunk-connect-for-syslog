from package.shared.pylib.parser_source_cache import psc_parse
from package.shared.pylib.parser_vps_cache import vpsc_parse


class MissingDatabase:
    def __getitem__(self, key):
        raise KeyError(key)


class CapturingLogger:
    def __init__(self):
        self.messages = []

    def debug(self, message):
        self.messages.append(message)


class LogMessage(dict):
    def get_as_str(self, key, default="", **kwargs):
        return self.get(key, default)


class RejectingLogMessage(LogMessage):
    def __setitem__(self, key, value):
        raise KeyError(key)


def make_name_cache_parser(database):
    parser = psc_parse()
    parser.db = database
    parser.logger = CapturingLogger()
    return parser


def make_vps_cache_parser(database):
    parser = vpsc_parse()
    parser.db = database
    parser.logger = CapturingLogger()
    return parser


def test_name_cache_miss_preserves_message_without_logging_traceback():
    parser = make_name_cache_parser(MissingDatabase())
    message = LogMessage(
        {
            "SOURCEIP": "192.0.2.10",
            "HOST": "192.0.2.10",
        }
    )

    assert parser.parse(message) is False
    assert message == {
        "SOURCEIP": "192.0.2.10",
        "HOST": "192.0.2.10",
    }
    assert parser.logger.messages == []


def test_name_cache_hit_applies_cached_host():
    parser = make_name_cache_parser({3221225994: "cache-host"})
    message = LogMessage(
        {
            "SOURCEIP": "192.0.2.10",
            "HOST": "192.0.2.10",
        }
    )

    assert parser.parse(message) is True
    assert message == {
        "SOURCEIP": "192.0.2.10",
        "HOST": "cache-host",
    }


def test_name_cache_unexpected_hit_failure_logs_traceback():
    parser = make_name_cache_parser({3221225994: "cache-host"})
    message = RejectingLogMessage(
        {
            "SOURCEIP": "192.0.2.10",
            "HOST": "192.0.2.10",
        }
    )

    assert parser.parse(message) is False
    assert "Traceback" in "\n".join(parser.logger.messages)


def test_vps_cache_miss_preserves_message_without_logging_traceback():
    parser = make_vps_cache_parser(MissingDatabase())
    message = LogMessage({"HOST": "cache-host"})

    assert parser.parse(message) is False
    assert message == {"HOST": "cache-host"}
    assert parser.logger.messages == []


def test_vps_cache_hit_applies_cached_fields():
    parser = make_vps_cache_parser(
        {
            "cache-host": {
                ".netsource.sc4s_vendor": "example",
                ".netsource.sc4s_product": "firewall",
            }
        }
    )
    message = LogMessage({"HOST": "cache-host"})

    assert parser.parse(message) is True
    assert message == {
        "HOST": "cache-host",
        ".netsource.sc4s_vendor": "example",
        ".netsource.sc4s_product": "firewall",
    }


def test_vps_cache_unexpected_hit_failure_logs_traceback():
    parser = make_vps_cache_parser(
        {
            "cache-host": {
                ".netsource.sc4s_vendor": "example",
                ".netsource.sc4s_product": "firewall",
            }
        }
    )
    message = RejectingLogMessage({"HOST": "cache-host"})

    assert parser.parse(message) is False
    assert "Traceback" in "\n".join(parser.logger.messages)
