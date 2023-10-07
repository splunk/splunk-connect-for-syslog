# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import shortuuid
import pytz

from jinja2 import Environment, select_autoescape, environment
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <78>Oct 25 09:10:00 /usr/sbin/cron[54928]: (root) CMD (/usr/libexec/atrun)
@pytest.mark.lite
def test_linux__nohost_program_as_path(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} /usr/sbin/cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix "[{{ pid }}]" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, pid=pid)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.lite
def test_linux__host_program_as_path(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} /usr/sbin/cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix "[{{ pid }}]" host={{ host }} sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, pid=pid, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.lite
def test_linux__nohost_program_conforms(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix "[{{ pid }}]" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, pid=pid)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.lite
def test_linux__host_program_conforms(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix "[{{ pid }}]" host={{ host }} sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, pid=pid, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
