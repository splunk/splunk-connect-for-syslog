# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest
env = Environment()


# 30: foo: 6340004: *Mar  4 11:45:20: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet
# 30: foo: *Apr 29 13:58:46.000001: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
# 30: foo: *Apr 29 13:58:46.411: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
# foo: *Apr 29 13:58:46.411: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.
# 30: foo: 6340004: Mar  4 11:45:20: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet
# 30: foo: Apr 29 13:58:46.000001: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
# 30: foo: Apr 29 13:58:46.411: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
# foo: Apr 29 13:58:46.411: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.
# foo: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the
# 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the
# foo: 1 2: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure.
# 101 21: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure.
# *Mar  1 18:48:50.483 UTC: %SYS-5-CONFIG_I: Configured from console by vty2 (10.34.195.36)

testdata = [
    "{{ mark }}{{ seq }}: {{ host }}: 6340004: *{{ bsd }}: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet",
    "{{ mark }}{{ seq }}: {{ host }}: *{{ bsd }}.{{ microsec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated {{ bsd }}.{{ millisec }}",
    "{{ mark }}{{ seq }}: {{ host }}: *{{ bsd }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: *{{ bsd }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.",
    "{{ mark }}{{ seq }}: {{ host }}: 6340004: {{ bsd }}: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ microsec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ millisec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: {{ bsd }}.{{ millisec }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure. {{ bsd }}.{{ millisec }}",
    "{{ mark }}*{{ bsd }}.{{ millisec }} {{ tzname }}: %SYS-5-CONFIG_I: Configured from console by vty2 (10.34.195.36) {{ host }}"
]

testdata_uptime = [
    "{{ mark }}{{ host }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the ",
    "{{ mark }}00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the {{ host }}",
    "{{ mark }}{{ host }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the ",
    "{{ mark }}{{ seq }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the {{ host }}",
    "{{ mark }}{{ seq }}: {{ host }}: 1 2: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure.",
    "{{ mark }}101 21: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure. {{ host }}"
]


@pytest.mark.parametrize("event", testdata)
def test_cisco_ios(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    time = time[:-7]
    millisec = iso[20:23]
    microsec = iso[20:26]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", seq=20, bsd=bsd, time=time,
                        millisec=millisec, microsec=microsec, tzname=tzname, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops (_time={{ epoch }} OR _time={{ epoch }}.{{ millisec }} OR _time={{ epoch }}.{{ microsec }}) sourcetype=\"cisco:ios\" (host=\"{{ host }}\" OR \"{{ host }}\")")
    search = st.render(epoch=epoch, millisec=millisec,
                       microsec=microsec, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_uptime)
def test_cisco_ios_uptime(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = get_host_key

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", seq=20, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops earliest=-1m@m latest=+1m@m sourcetype=\"cisco:ios\" (host=\"{{ host }}\" OR \"{{ host }}\")")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
