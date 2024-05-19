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
import random
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


# RP/0/RP0/CPU0:Oct 20 17:14:37.407 UTC: config[65539]: %MGBL-CONFIGCLI-3-COMMIT_FAILURE : Configuration commit running under 'vty0': by :'core' failed,commit results stored in '/cfs/cfg/lr/failed/seamless/1000000007_failed.cfg'
# RP/0/RP0/CPU0:Oct 20 17:42:15.454 UTC: plat_sl_client[147]: %LICENSE-PLAT_CLIENT-2-SIA_INSUFFICIENT_LICENSE : Number of SIA license(s) used is more than available. SW Upgrade will still be allowed as SIA Grace Period is remaining
# RP/0/RP0/CPU0:Oct 20 18:41:50.646 UTC: config[67105]: %MGBL-SYS-5-CONFIG_I : Configured from console by core on vty0 (10.0.1.100)
# RP/0/RP0/CPU0:Oct 20 19:34:46.088 UTC: nfsvr[317]: %MGBL-NETFLOW-6-INFO_CACHE_SIZE_EXCEEDED : Cache size of 65535 for monitor NETFLOW has been exceeded
# RP/0/RP0/CPU0:Oct 20 19:39:57.914 UTC: ssh_syslog_proxy[1214]: %SECURITY-SSHD_SYSLOG_PRX-6-INFO_GENERAL : sshd[39770]: Failed authentication/pam for <unknown> from 10.0.1.100 port 48906 ssh2
testdata = [
    "{{ mark }}{{ node_id }}:{{ bsd }}: config[65539]: %MGBL-CONFIGCLI-3-COMMIT_FAILURE : Configuration commit running under 'vty0': by :'core' failed,commit results stored in '/cfs/cfg/lr/failed/seamless/1000000007_failed.cfg",
    "{{ mark }}{{ node_id }}:{{ bsd }}: plat_sl_client[147]: %LICENSE-PLAT_CLIENT-2-SIA_INSUFFICIENT_LICENSE : Number of SIA license(s) used is more than available. SW Upgrade will still be allowed as SIA Grace Period is remaining",
    "{{ mark }}{{ node_id }}:{{ bsd }}: config[67105]: %MGBL-SYS-5-CONFIG_I : Configured from console by core on vty0 (10.0.1.100)",
    "{{ mark }}{{ node_id }}:{{ bsd }}: nfsvr[317]: %MGBL-NETFLOW-6-INFO_CACHE_SIZE_EXCEEDED : Cache size of 65535 for monitor NETFLOW has been exceeded",
    "{{ mark }}{{ node_id }}:{{ bsd }}: ssh_syslog_proxy[1214]: %SECURITY-SSHD_SYSLOG_PRX-6-INFO_GENERAL : sshd[39770]: Failed authentication/pam for <unknown> from 10.0.1.100 port 48906 ssh2"
]

@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("cisco")
def test_cisco_ios_xr(
    record_property, setup_splunk, setup_sc4s, event
):
    random_number = lambda max: random.randint(0, max)
    node_id = f"RP/{random_number(4)}/RP{random_number(4)}/CPU{random_number(4)}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<166>",
        node_id=node_id,
        bsd=bsd
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    category_group = "-".join(message.split("%")[1].split("-")[:2])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="cisco:xr" {{distinction}}'
    )
    search = st.render(epoch=epoch, distinction=category_group)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# <190>290692: HOST_NAME RP/0/RSP0/CPU0:Mar 26 14:47:02.754 : SSHD_[65935]: %SECURITY-SSHD-6-INFO_USER_LOGOUT : User 'HELLO' from '8.8.8.8' logged out on 'vty0'
@pytest.mark.addons("cisco")
def test_cisco_ios_xr_hostname_with_underscore(
    record_property, setup_splunk, setup_sc4s
):
    random_number = lambda max: random.randint(0, max)
    node_id = f"RP/{random_number(4)}/RP{random_number(4)}/CPU{random_number(4)}"
    hostname = "HOST_NAME"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    event = "{{ mark }}290692: {{hostname}} {{ node_id }}:{{ bsd }} : SSHD_[65935]: %SECURITY-SSHD-6-INFO_USER_LOGOUT : User 'HELLO' from '8.8.8.8' logged out on 'vty0'"

    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<166>",
        hostname=hostname,
        node_id=node_id,
        bsd=bsd
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="cisco:xr" host={{hostname}}'
    )
    search = st.render(epoch=epoch, hostname=hostname)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1