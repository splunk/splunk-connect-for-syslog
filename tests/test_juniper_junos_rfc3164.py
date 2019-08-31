# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])
# <23> Mar 18 17:56:52 RT_UTM: WEBFILTER_URL_PERMITTED: WebFilter: ACTION="URL Permitted" 192.168.32.1(62054)->1.1.1.1(443) CATEGORY="Enhanced_Information_Technology" REASON="BY_PRE_DEFINED" PROFILE="UTM-Wireless-Profile" URL=ent-shasta-rrs.symantec.com OBJ=/ username N/A roles N/A
def test_juniper_utm_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} RT_UTM: WEBFILTER_URL_PERMITTED: WebFilter: ACTION=\"URL Permitted\" 192.168.32.1(62054)->1.1.1.1(443) CATEGORY=\"Enhanced_Information_Technology\" REASON=\"BY_PRE_DEFINED\" PROFILE=\"UTM-Wireless-Profile\" URL=ent-shasta-rrs.symantec.com OBJ=/ username N/A roles N/A")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netids host=\"{{ host }}\" sourcetype=\"juniper:junos:firewall\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <23> Nov 18 09:56:58  INTERNET-ROUTER RT_FLOW: RT_FLOW_SESSION_CREATE: session created 192.168.1.102/58662->8.8.8.8/53 junos-dns-udp 68.144.1.1/55893->8.8.8.8/53 TRUST-INET-ACCESS None 17 OUTBOUND-INTERNET-ACCESS TRUST INTERNET 6316 N/A(N/A) vlan.192
def test_juniper_firewall_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} RT_FLOW: RT_FLOW_SESSION_CREATE: session created 192.168.1.102/58662->8.8.8.8/53 junos-dns-udp 68.144.1.1/55893->8.8.8.8/53 TRUST-INET-ACCESS None 17 OUTBOUND-INTERNET-ACCESS TRUST INTERNET 6316 N/A(N/A) vlan.192")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"juniper:junos:firewall\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <23> Feb 27 15:00:00 vpn-001 Juniper: 2013-02-27 15:00:00 - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[] - Session timed out for xxx@xxx.xxx.xxx/Users (session:00000000) due to inactivity (last access at 13:59:31 2013/02/27). Idle session identified during routine system scan.
# <23> Feb 27 15:00:00 vpn-001 Juniper: 2013-02-27 15:00:00 - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[User_Role] - Remote address for user xxx@xxx.xxx/Users changed from 000.000.000.000 to 000.000.000.000. Access denied.
def test_juniper_sslvpn_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} Juniper: {% now 'utc', '%Y-%m-%d %H:%M:%S' %} - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[User_Role] - Remote address for user xxx@xxx.xxx/Users changed from 000.000.000.000 to 000.000.000.000. Access denied.")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"juniper:sslvpn\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1



def test_juniper_idp_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} RT_IDP: IDP_ATTACK_LOG_EVENT: IDP: at 1303673404, ANOMALY Attack log <64.1.2.1/48397->198.87.233.110/80> for TCP protocol and service HTTP application NONE by rule 3 of rulebase IPS in policy Recommended. attack: repeat=0, action=DROP, threat-severity=HIGH, name=HTTP:INVALID:MSNG-HTTP-VER, NAT <46.0.3.254:55870->0.0.0.0:0>, time-elapsed=0, inbytes=0, outbytes=0, inpackets=0, outpackets=0, intf:trust:fe-0/0/2.0->untrust:fe-0/0/3.0, packet-log-id: 0 and misc-message -")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netids host=\"{{ host }}\" sourcetype=\"juniper:junos:idp\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
