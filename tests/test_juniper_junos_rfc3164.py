# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape
from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <23> Mar 18 17:56:52 RT_UTM: WEBFILTER_URL_PERMITTED: WebFilter: ACTION="URL Permitted" 192.168.32.1(62054)->1.1.1.1(443) CATEGORY="Enhanced_Information_Technology" REASON="BY_PRE_DEFINED" PROFILE="UTM-Wireless-Profile" URL=ent-shasta-rrs.symantec.com OBJ=/ username N/A roles N/A
@pytest.mark.addons("juniper")
def test_juniper_utm_standard(record_property, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} RT_UTM: WEBFILTER_URL_PERMITTED: WebFilter: ACTION="URL Permitted" 192.168.32.1(62054)->1.1.1.1(443) CATEGORY="Enhanced_Information_Technology" REASON="BY_PRE_DEFINED" PROFILE="UTM-Wireless-Profile" URL=ent-shasta-rrs.symantec.com OBJ=/ username N/A roles N/A'
    )
    message = mt.render(mark="<23>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="juniper:junos:firewall"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <23> Nov 18 09:56:58  INTERNET-ROUTER RT_FLOW: RT_FLOW_SESSION_CREATE: session created 192.168.1.102/58662->8.8.8.8/53 junos-dns-udp 68.144.1.1/55893->8.8.8.8/53 TRUST-INET-ACCESS None 17 OUTBOUND-INTERNET-ACCESS TRUST INTERNET 6316 N/A(N/A) vlan.192
@pytest.mark.addons("juniper")
def test_juniper_firewall_standard(
    record_property, get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} RT_FLOW: RT_FLOW_SESSION_CREATE: session created 192.168.1.102/58662->8.8.8.8/53 junos-dns-udp 68.144.1.1/55893->8.8.8.8/53 TRUST-INET-ACCESS None 17 OUTBOUND-INTERNET-ACCESS TRUST INTERNET 6316 N/A(N/A) vlan.192"
    )
    message = mt.render(mark="<23>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="juniper:junos:firewall"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("juniper")
def test_juniper_idp_standard(record_property, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} RT_IDP: IDP_ATTACK_LOG_EVENT: IDP: at 1303673404, ANOMALY Attack log <64.1.2.1/48397->198.87.233.110/80> for TCP protocol and service HTTP application NONE by rule 3 of rulebase IPS in policy Recommended. attack: repeat=0, action=DROP, threat-severity=HIGH, name=HTTP:INVALID:MSNG-HTTP-VER, NAT <46.0.3.254:55870->0.0.0.0:0>, time-elapsed=0, inbytes=0, outbytes=0, inpackets=0, outpackets=0, intf:trust:fe-0/0/2.0->untrust:fe-0/0/3.0, packet-log-id: 0 and misc-message -"
    )
    message = mt.render(mark="<23>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="juniper:junos:idp"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_junos_snmp = [
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: SNMP_TRAP_LINK_UP: ifIndex 584, ifAdminStatus up(1), ifOperStatus up(1), ifName ge-0/0/45",
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: SNMP_TRAP_LINK_DOWN: ifIndex 584, ifAdminStatus up(1), ifOperStatus down(2), ifName ge-0/0/45",
]
# <165>1 2007-02-15T09:17:15.719Z mib2d[1484]: SNMP_TRAP_LINK_UP: ifIndex 584, ifAdminStatus up(1), ifOperStatus up(1), ifName ge-0/0/45
# @pytest.mark.xfail
@pytest.mark.addons("juniper")
@pytest.mark.parametrize("event", testdata_junos_snmp)
def test_juniper_junos_snmp(
    record_property, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<23>", bsd=bsd, host=host, app="mib2d[1484]")
    message1 = mt.render(mark="", bsd="", host="", app="mib2d[1484]")
    message1 = message1.lstrip()
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="juniper:junos:snmp" _raw="{{ message }}"'
    )
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_junos_firewall_switch = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: ESWD_STP_STATE_CHANGE_INFO: STP state for interface ge-0/0/45.0 context id 0 changed from FORWARDING to BLOCKING",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: ESWD_DAI_FAILED: 12 ARP_REQUEST received, interface ge-0/0/8.0[index 76], vlan __pvlan_PRI-C-RES_ge-0/0/8.0__[index 14], sender ip/mac 10.43.16.17/b8:27:eb:53:a4:e2, receiver ip/mac 10.43.16.1/00:00:00:00:00:00 ",
]
# @pytest.mark.xfail
@pytest.mark.addons("juniper")
@pytest.mark.parametrize("event", testdata_junos_firewall_switch)
def test_juniper_junos_switch(
    record_property, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<23>", bsd=bsd, host=host, app="eswd[1473]")

    message1 = mt.render(mark="", bsd="", host="", app="eswd[1473]")
    message1 = message1.lstrip()
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="juniper:junos:firewall" _raw="{{ message }}"'
    )
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_junos_firewall_router = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: PFE_FW_SYSLOG_ETH_IP: FW: xe-0/0/3.0   A XXXX 40:00:3d:06:f6:1d -> 45:00:00:28:2e:05  tcp 194.170.173.252 172.65.252.196 36146  9037 (1 packets)",
]
# <165>1 2007-02-15T09:17:15.719Z tfeb0 PFE_FW_SYSLOG_ETH_IP: FW: xe-0/0/3.0   A XXXX 40:00:3d:06:f6:1d -> 45:00:00:28:2e:05  tcp 194.170.173.252 172.65.252.196 36146  9037 (1 packets)
# @pytest.mark.xfail
@pytest.mark.parametrize("event", testdata_junos_firewall_router)
@pytest.mark.addons("juniper")
def test_juniper_junos_router(
    record_property, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, app="tfeb0")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="juniper:junos:firewall" '
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_junos_switch_rpd = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: EVENT <UpDown> ge-2/0/30.0 index 2147404488 <Up Broadcast Multicast> address #0 b0.a8.6e.9e.ad.a1",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: EVENT <Bandwidth UpDown> ge-1/0/4 index 181 <Up Broadcast Multicast> address #0 3c.61.4.6a.22.7",
]
# <165>1 2007-02-15T09:17:15.719Z rpd[1341]: EVENT <Bandwidth UpDown> ge-1/0/4 index 181 <Up Broadcast Multicast> address #0 3c.61.4.6a.22.7
# @pytest.mark.xfail
@pytest.mark.addons("juniper")
@pytest.mark.parametrize("event", testdata_junos_switch_rpd)
def test_juniper_junos_switch_rpd(
    record_property, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="rpd[1473]")

    message1 = mt.render(mark="", bsd="", host="", app="rpd[1473]")
    message1 = message1.lstrip()
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="juniper:junos:firewall" _raw="{{ message }}"'
    )
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <161>Mar 18 17:56:52 host RT_SYSTEM: RTLOG_CONN_ERROR: Connection error tcp_10.181.123.45 Error code: major 3 minor 1 code 110, description:TCP timed out after SYN is sent out
@pytest.mark.addons("juniper")
def test_juniper_system_standard(
    record_property, get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} RT_SYSTEM: RTLOG_CONN_ERROR: Connection error tcp_10.181.123.45 Error code: major 3 minor 1 code 110, description:TCP timed out after SYN is sent out "
    )
    message = mt.render(mark="<161>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="juniper:legacy"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
