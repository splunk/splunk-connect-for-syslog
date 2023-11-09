# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest
import shortuuid

env = Environment(autoescape=select_autoescape(default_for_string=False))


# 30: foo: 6340004: *Mar  4 11:45:20: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet
# 30: foo: *Apr 29 13:58:46.000001: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
# 30: foo: *Apr 29 13:58:46.411: %SYS-6-LOGGINGHOST_START   STOP: Logging to host 192.168.1.239 stopped - CLI initiated
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
# <132>xxxxx: *spamApTask1: May 26 18:52:01.958: %CAPWAP-4-DISC_INTF_ERR2: [PA]capwap_ac_sm.c:2053 Ignoring Primary discovery request received on a wrong VLAN (202) on interface (8) from AP 00:b7:00:00:00:00
testdata = [
    "{{ mark }}{{ seq }}: {{ host }}: 6340004: {{ bsd }}: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ microsec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated {{ bsd }}.{{ millisec }}",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: {{ bsd }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ millisec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: {{ bsd }}.{{ millisec }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure. {{ bsd }}.{{ millisec }}",
    "{{ mark }}{{ host }}: *spamApTask1: {{ bsd }}.{{ millisec }}: %CAPWAP-4-DISC_INTF_ERR2: [PA]capwap_ac_sm.c:2053 Ignoring Primary discovery request received on a wrong VLAN (202) on interface (8) from AP 00:b7:00:00:00:00",
    "{{ mark }}22191: {{ host }}: 022546: {{ bsd }}.{{ millisec }} CDT: %PARSER-5-CFGLOG_LOGGEDCMD: User:dfa_service_admin  logged command:!exec: enable",
    "{{ mark }}{{ host }}: {{ year }} {{ bsd }}.{{ millisec }} CDT: %MODULE-2-MOD_SOMEPORTS_FAILED: Module 13 (Serial number: JAF12345678) reported failure on ports Eth13/17-20 (Ethernet) due to hardware not accessible in device DEV_CLP_FWD(device error 0xca804200)",
    "{{ mark }}{{ bsd }}.{{ millisec }} {{ tzname }}: %SYS-5-CONFIG_I: Configured from console by vty2 (10.34.195.36) {{ host }}",
    "{{ mark }}84027: {{ bsd }}.{{ millisec }} DST: %SYS-5-CONFIG_I: Configured from console by username on vty0 ({{ host }})",
    "{{ mark }}{{ host }}: {{ year }} {{ bsd }} CDT: %MODULE-2-MOD_SOMEPORTS_FAILED: Module 13 (Serial number: JAF12345678) reported failure on ports Eth13/17-20 (Ethernet) due to hardware not accessible in device DEV_CLP_FWD(device error 0xca804200)",
    "{{ mark }}: 2020 {{ bsd }} EDT: %L2FM-4-L2FM_MAC_MOVE: Mac e4c7.2266.f741 in vlan 1159 has moved from  100.16.4513 to  {{ host }}",
]
testdata_badtime = [
    "{{ mark }}{{ seq }}: {{ host }}: 6340004: *{{ bsd }}: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet",
    "{{ mark }}{{ seq }}: {{ host }}: *{{ bsd }}.{{ microsec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated {{ bsd }}.{{ millisec }}",
    "{{ mark }}{{ seq }}: {{ host }}: *{{ bsd }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: *{{ bsd }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.",
    "{{ mark }}{{ seq }}: {{ host }}: 6340004: {{ bsd }}: %SEC-6-IPACCESSLOGP: list INET-BLOCK permitted tcp 192.168.20.252(55244) -> 10.54.3.178(44818), 1 packet",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ microsec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ seq }}: {{ host }}: {{ bsd }}.{{ millisec }}: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated",
    "{{ mark }}{{ host }}: {{ bsd }}.{{ millisec }}: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure. {{ bsd }}.{{ millisec }}",
    "{{ mark }}*{{ bsd }}.{{ millisec }} {{ tzname }}: %SYS-5-CONFIG_I: Configured from console by vty2 (10.34.195.36) {{ host }}",
    "{{ mark }}84027: {{ bsd }}.{{ millisec }} DST: %SYS-5-CONFIG_I: Configured from console by username on vty0 ({{ host }})",
    "{{ mark }}{{ host }}: *spamApTask1: {{ bsd }}.{{ millisec }}: %CAPWAP-4-DISC_INTF_ERR2: [PA]capwap_ac_sm.c:2053 Ignoring Primary discovery request received on a wrong VLAN (202) on interface (8) from AP 00:b7:00:00:00:00",
    "{{ mark }}22191: {{ host }}: 022546: .{{ bsd }}.{{ millisec }} CDT: %PARSER-5-CFGLOG_LOGGEDCMD: User:dfa_service_admin  logged command:!exec: enable",
    "{{ mark }}: {{ year }} {{ bsd }} PDT: %DAEMON-3-SYSTEM_MSG: ftp disabled, removing - xinetd[4930] {{ host }}",
]

testdata_uptime = [
    "{{ mark }}{{ host }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the ",
    "{{ mark }}00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the {{ host }}",
    "{{ mark }}{{ host }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the ",
    "{{ mark }}{{ seq }}: 00:01:01: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the {{ host }}",
    "{{ mark }}{{ seq }}: {{ host }}: 1 2: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure.",
    "{{ mark }}101 21: %SYSMGR-STANDBY-3-SHUTDOWN_START: The System Manager has started the shutdown procedure.shutdown procedure. {{ host }}",
]


@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("cisco")
def test_cisco_ios(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, _, _, tzname, epoch = time_operations(dt)
    year = dt.year

    # Tune time functions
    epoch = epoch[:-7]
    time = time[:-7]
    millisec = iso[20:23]
    microsec = iso[20:26]

    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<166>",
        seq=20,
        bsd=bsd,
        time=time,
        millisec=millisec,
        microsec=microsec,
        tzname=tzname,
        host=host,
        year=year,
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops (_time={{ epoch }} OR _time={{ epoch }}.{{ millisec }} OR _time={{ epoch }}.{{ microsec }}) sourcetype="cisco:ios" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, millisec=millisec, microsec=microsec, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_badtime)
@pytest.mark.addons("cisco")
def test_cisco_ios_badtime(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, _, _, tzname, epoch = time_operations(dt)
    year = dt.year

    # Tune time functions
    epoch = epoch[:-7]
    time = time[:-7]
    millisec = iso[20:23]
    microsec = iso[20:26]

    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<166>",
        seq=20,
        bsd=bsd,
        time=time,
        millisec=millisec,
        microsec=microsec,
        year=year,
        tzname=tzname,
        host=host,
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops earliest=-1m@m latest=+1m@m sourcetype="cisco:ios" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_uptime)
@pytest.mark.addons("cisco")
def test_cisco_ios_uptime(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", seq=20, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops earliest=-1m@m latest=+1m@m sourcetype="cisco:ios" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_nx_os_soup(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} %MODULE-5-MOD_OK: Module 1 is online"
    )
    message = mt.render(
        mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ios"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <187>364241: May 19 16:58:44.814 GMT: %ADJ-3-RESOLVE_REQ: Adj resolve request: Failed to resolve 1.1.1.1 Vlan1
@pytest.mark.addons("cisco")
def test_cisco_nx_os_soup2(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}364241: {{ bsd }} GMT: %ADJ-3-RESOLVE_REQ: Adj resolve request: Failed to resolve {{ host }} Vlan1\n"
    )
    message = mt.render(
        mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} host!=GMT index=netops sourcetype="cisco:ios" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#%ADJ-3-RESOLVE_REQ
# Nov 1 14:07:58 excal-113 %MODULE-5-MOD_OK: Module 1 is online
# @pytest.mark.xfail
# def test_cisco_nx_os_singleport(record_property,  get_host_key, setup_splunk, setup_sc4s):
#    host = get_host_key
#
#    dt = datetime.datetime.now()
#    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
#
#    # Tune time functions
#    epoch = epoch[:-7]
#
#    mt = env.from_string(
#        "{{ mark }} {{ bsd }} {{ host }} %MODULE-5-MOD_OK: Module 1 is online")
#    message = mt.render(mark="<23>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
#
#    sendsingle(message, host="sc4s-nx-os")
#
#    st = env.from_string("search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ios\"")
#    search = st.render(epoch=epoch, host=host)
#
#    result_count, _ = splunk_single(setup_splunk, search)
#
#    record_property("host", host)
#    record_property("resultCount", result_count)
#    record_property("message", message)
#
#    assert result_count == 1

# <11>July 22 22:45:28 apic1 %LOG_LOCAL0-2-SYSTEM_MSG [F0110][soaking][node-failed][critical][topology/pod-1/node-102/fault-F0110] Node 102 not reachable. unknown
@pytest.mark.addons("cisco")
def test_cisco_aci_loglocal(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Cisco APIC
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} %LOG_LOCAL0-2-SYSTEM_MSG [F0110][soaking][node-failed][critical][topology/pod-1/node-102/fault-F0110]\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ios"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_aci_log(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Cisco APIC
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} %LOG_-2-SYSTEM_MSG [F0110][soaking][node-failed][critical][topology/pod-1/node-102/fault-F0110]\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ios"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#%ACLLOG-5-ACLLOG_PKTLOG
@pytest.mark.addons("cisco")
def test_cisco_aci_acl(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Cisco APIC
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} %ACLLOG-5-ACLLOG_PKTLOG unable to locate real message\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ios"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
