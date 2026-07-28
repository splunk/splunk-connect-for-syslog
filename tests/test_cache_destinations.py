from types import SimpleNamespace
from unittest.mock import sentinel

import pytest
from sqlitedict import SqliteDict

from package.shared.pylib import parser_source_cache, parser_vps_cache
from package.shared.pylib.parser_source_cache import psc_dest
from package.shared.pylib.parser_vps_cache import vpsc_dest

QUEUED = sentinel.QUEUED
SUCCESS = sentinel.SUCCESS
ERROR = sentinel.ERROR


class CapturingLogger:
    def __init__(self):
        self.messages = []

    def debug(self, message):
        self.messages.append(message)


class LogMessage(dict):
    def get_as_str(self, key, default="", **kwargs):
        return self.get(key, default)


class FailingReadDatabase:
    def __getitem__(self, key):
        raise RuntimeError("read failed")


class FailingCommitDatabase:
    def commit(self):
        raise RuntimeError("commit failed")


def set_destination_statuses(destination):
    destination.QUEUED = QUEUED
    destination.SUCCESS = SUCCESS
    destination.ERROR = ERROR


def make_name_cache_lifecycle_destination(monkeypatch, tmp_path):
    database_path = tmp_path / "name-cache"
    monkeypatch.setattr(
        parser_source_cache,
        "syslogng",
        SimpleNamespace(Logger=CapturingLogger),
        raising=False,
    )
    monkeypatch.setattr(parser_source_cache, "hostdict", str(database_path))

    destination = psc_dest()
    set_destination_statuses(destination)
    return destination, f"{database_path}.sqlite"


def make_vps_cache_lifecycle_destination(monkeypatch, tmp_path):
    database_path = tmp_path / "vps-cache"
    monkeypatch.setattr(
        parser_vps_cache,
        "syslogng",
        SimpleNamespace(Logger=CapturingLogger),
        raising=False,
    )
    monkeypatch.setattr(parser_vps_cache, "hostdict", str(database_path))

    destination = vpsc_dest()
    set_destination_statuses(destination)
    return destination, f"{database_path}.sqlite"


def make_name_cache_sender(database):
    destination = psc_dest()
    destination.db = database
    destination.logger = CapturingLogger()
    set_destination_statuses(destination)
    return destination


def make_vps_cache_sender(database):
    destination = vpsc_dest()
    destination.db = database
    destination.logger = CapturingLogger()
    set_destination_statuses(destination)
    return destination


def test_name_cache_destination_opens_and_closes_database(
    monkeypatch,
    tmp_path,
):
    destination, _ = make_name_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )

    assert destination.init({}) is True
    assert destination.db is None
    assert destination.open() is True
    assert destination.db is not None

    destination.deinit()

    assert destination.db is None
    destination.close()
    assert destination.db is None


def test_name_cache_new_entry_is_published_only_when_batch_is_flushed(
    monkeypatch,
    tmp_path,
):
    destination, database_file = make_name_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True
    assert destination.open() is True
    reader = SqliteDict(database_file, outer_stack=False)
    database_key = 3221225986

    try:
        result = destination.send(
            LogMessage(
                {
                    "SOURCEIP": "192.0.2.2",
                    "HOST": "cache-host",
                }
            )
        )

        assert result is QUEUED
        with pytest.raises(KeyError):
            reader[database_key]

        assert destination.flush() is SUCCESS
        assert reader[database_key] == "cache-host"
    finally:
        reader.close()
        destination.close()


def test_name_cache_changed_entry_is_published_only_after_flush(
    monkeypatch,
    tmp_path,
):
    destination, database_file = make_name_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True
    assert destination.open() is True
    database_key = 3221225986
    destination.db[database_key] = "old-cache-host"
    destination.db.commit()
    reader = SqliteDict(database_file, outer_stack=False)

    try:
        result = destination.send(
            LogMessage(
                {
                    "SOURCEIP": "192.0.2.2",
                    "HOST": "cache-host",
                }
            )
        )

        assert result is QUEUED
        assert reader[database_key] == "old-cache-host"

        assert destination.flush() is SUCCESS
        assert reader[database_key] == "cache-host"
    finally:
        reader.close()
        destination.close()


@pytest.mark.parametrize(
    "message",
    [
        pytest.param(
            {"HOST": "cache-host"},
            id="missing-source-ip",
        ),
        pytest.param(
            {"SOURCEIP": "", "HOST": "cache-host"},
            id="empty-source-ip",
        ),
        pytest.param(
            {"SOURCEIP": "192.0.2.2"},
            id="missing-host",
        ),
        pytest.param(
            {"SOURCEIP": "192.0.2.2", "HOST": ""},
            id="empty-host",
        ),
        pytest.param(
            {
                "SOURCEIP": "not-an-ip-address",
                "HOST": "cache-host",
            },
            id="invalid-source-ip",
        ),
    ],
)
def test_name_cache_invalid_key_is_successful_noop(message):
    destination = make_name_cache_sender({})

    result = destination.send(LogMessage(message))

    assert result is SUCCESS
    assert destination.db == {}


def test_name_cache_database_read_failure_returns_error():
    database = FailingReadDatabase()
    destination = make_name_cache_sender(database)

    result = destination.send(
        LogMessage(
            {
                "SOURCEIP": "192.0.2.2",
                "HOST": "cache-host",
            }
        )
    )

    assert result is ERROR


def test_name_cache_commit_failure_returns_error():
    database = FailingCommitDatabase()
    destination = make_name_cache_sender(database)

    assert destination.flush() is ERROR


def test_name_cache_database_open_failure_returns_false(
    monkeypatch,
    tmp_path,
):
    destination, _ = make_name_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True

    def fail_to_open(*args, **kwargs):
        raise RuntimeError("open failed")

    monkeypatch.setattr(parser_source_cache, "SqliteDict", fail_to_open)

    assert destination.open() is False
    assert destination.db is None


def test_vps_cache_destination_opens_and_closes_database(
    monkeypatch,
    tmp_path,
):
    destination, _ = make_vps_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )

    assert destination.init({}) is True
    assert destination.db is None
    assert destination.open() is True
    assert destination.db is not None

    destination.deinit()

    assert destination.db is None
    destination.close()
    assert destination.db is None


def test_vps_cache_new_entry_is_published_only_when_batch_is_flushed(
    monkeypatch,
    tmp_path,
):
    destination, database_file = make_vps_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True
    assert destination.open() is True
    reader = SqliteDict(database_file, outer_stack=False)
    expected_fields = {
        ".netsource.sc4s_vendor": "example",
        ".netsource.sc4s_product": "firewall",
    }

    try:
        result = destination.send(
            LogMessage(
                {
                    "HOST": "cache-host",
                    "fields.sc4s_vendor": "example",
                    "fields.sc4s_product": "firewall",
                }
            )
        )

        assert result is QUEUED
        with pytest.raises(KeyError):
            reader["cache-host"]

        assert destination.flush() is SUCCESS
        assert reader["cache-host"] == expected_fields
    finally:
        reader.close()
        destination.close()


def test_vps_cache_changed_entry_is_published_only_after_flush(
    monkeypatch,
    tmp_path,
):
    destination, database_file = make_vps_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True
    assert destination.open() is True
    old_fields = {
        ".netsource.sc4s_vendor": "old-vendor",
        ".netsource.sc4s_product": "old-product",
    }
    expected_fields = {
        ".netsource.sc4s_vendor": "example",
        ".netsource.sc4s_product": "firewall",
    }
    destination.db["cache-host"] = old_fields
    destination.db.commit()
    reader = SqliteDict(database_file, outer_stack=False)

    try:
        result = destination.send(
            LogMessage(
                {
                    "HOST": "cache-host",
                    "fields.sc4s_vendor": "example",
                    "fields.sc4s_product": "firewall",
                }
            )
        )

        assert result is QUEUED
        assert reader["cache-host"] == old_fields

        assert destination.flush() is SUCCESS
        assert reader["cache-host"] == expected_fields
    finally:
        reader.close()
        destination.close()


@pytest.mark.parametrize(
    "message",
    [
        pytest.param({}, id="missing-host"),
        pytest.param({"HOST": ""}, id="empty-host"),
    ],
)
def test_vps_cache_invalid_key_is_successful_noop(message):
    destination = make_vps_cache_sender({})

    result = destination.send(LogMessage(message))

    assert result is SUCCESS
    assert destination.db == {}


def test_vps_cache_database_read_failure_returns_error():
    database = FailingReadDatabase()
    destination = make_vps_cache_sender(database)

    result = destination.send(
        LogMessage(
            {
                "HOST": "cache-host",
                "fields.sc4s_vendor": "example",
                "fields.sc4s_product": "firewall",
            }
        )
    )

    assert result is ERROR


def test_vps_cache_commit_failure_returns_error():
    database = FailingCommitDatabase()
    destination = make_vps_cache_sender(database)

    assert destination.flush() is ERROR


def test_vps_cache_database_open_failure_returns_false(
    monkeypatch,
    tmp_path,
):
    destination, _ = make_vps_cache_lifecycle_destination(
        monkeypatch,
        tmp_path,
    )
    assert destination.init({}) is True

    def fail_to_open(*args, **kwargs):
        raise RuntimeError("open failed")

    monkeypatch.setattr(parser_vps_cache, "SqliteDict", fail_to_open)

    assert destination.open() is False
    assert destination.db is None
