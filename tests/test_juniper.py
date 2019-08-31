# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


# <134> Aug 02 14:45:04 10.0.0.1 65.197.254.193 20090320, 17331, 2009/03/20 14:47:45, 2009/03/20 14:47:50, global, 53, [FW NAME], [FW IP], traffic, traffic log, trust, (NULL), 10.1.1.20, 1725, 82.2.19.2, 2383, untrust, (NULL), 84.5.78.4, 80, 84.53.178.64, 80, tcp, global, 53, [FW NAME], fw/vpn, 4, accepted, info, no, Creation, (NULL), (NULL), (NULL), 0, 0, 0, 0, 0, 0, 0, 1, no, 0, Not Set, sos
def test_juniper_nsm_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} jnpnsm-{{ host }} 65.197.254.193 20090320, 17331, 2009/03/20 14:47:45, 2009/03/20 14:47:50, global, 53, [FW NAME], [FW IP], traffic, traffic log, trust, (NULL), 10.1.1.20, 1725, 82.2.19.2, 2383, untrust, (NULL), 84.5.78.4, 80, 84.53.178.64, 80, tcp, global, 53, [FW NAME], fw/vpn, 4, accepted, info, no, Creation, (NULL), (NULL), (NULL), 0, 0, 0, 0, 0, 0, 0, 1, no, 0, Not Set, sos")
    message = mt.render(mark="<134>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"jnpnsm-{{ host }}\" sourcetype=\"juniper:nsm\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# THE LOG SAMPLE BELOW IS IMPLIED FROM THE JUNIPER DOCS; need to obtain a real sample.
# <134> Aug 02 14:45:04 10.0.0.1 65.197.254.193 20090320, 17331, 2009/03/20 14:47:45, 2009/03/20 14:47:50, global, 53, [IDP NAME], [IDP IP], predefined, rule, trust, (NULL), 10.1.1.20, 1725, 82.2.19.2, 2383, untrust, (NULL), 84.5.78.4, 80, 84.53.178.64, 80, tcp, global, 53, [IDP NAME], fw/vpn, 4, accepted, info, no, Creation, (NULL), (NULL), (NULL), 0, 0, 0, 0, 0, 0, 0, 1, no, 0, Not Set, sos
def test_juniper_nsm_idp_standard(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} jnpnsmidp-{{ host }} 65.197.254.193 20090320, 17331, 2009/03/20 14:47:45, 2009/03/20 14:47:50, global, 53, [IDP NAME], [IDP IP], predefined, rule, trust, (NULL), 10.1.1.20, 1725, 82.2.19.2, 2383, untrust, (NULL), 84.5.78.4, 80, 84.53.178.64, 80, tcp, global, 53, [IDP NAME], fw/vpn, 4, accepted, info, no, Creation, (NULL), (NULL), (NULL), 0, 0, 0, 0, 0, 0, 0, 1, no, 0, Not Set, sos")
    message = mt.render(mark="<134>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netids host=\"jnpnsmidp-{{ host }}\" sourcetype=\"juniper:nsm:idp\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <23> Apr 24 12:30:05  cs-loki3 RT_IDP: IDP_ATTACK_LOG_EVENT: IDP: at 1303673404, ANOMALY Attack log <64.1.2.1/48397->198.87.233.110/80> for TCP protocol and service HTTP application NONE by rule 3 of rulebase IPS in policy Recommended. attack: repeat=0, action=DROP, threat-severity=HIGH, name=HTTP:INVALID:MSNG-HTTP-VER, NAT <46.0.3.254:55870->0.0.0.0:0>, time-elapsed=0, inbytes=0, outbytes=0, inpackets=0, outpackets=0, intf:trust:fe-0/0/2.0->untrust:fe-0/0/3.0, packet-log-id: 0 and misc-message -
# <23> Mar 18 17:56:52 [FW IP] [FW Model]: NetScreen device_id=netscreen2  [Root]system-notification-00257(traffic): start_time="2009-03-18 16:07:06" duration=0 policy_id=320001 service=msrpc Endpoint Mapper(tcp) proto=6 src zone=Null dst zone=self action=Deny sent=0 rcvd=16384 src=21.10.90.125 dst=23.16.1.1
def test_juniper_netscreen(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} jnpns-{{ host }} ns204: NetScreen device_id=netscreen2  [Root]system-notification-00257(traffic): start_time=\"2009-03-18 16:07:06\" duration=0 policy_id=320001 service=msrpc Endpoint Mapper(tcp) proto=6 src zone=Null dst zone=self action=Deny sent=0 rcvd=16384 src=21.10.90.125 dst=23.16.1.1\n")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"jnpns-{{ host }}\" sourcetype=\"netscreen:firewall\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <23> Apr 24 12:30:05  cs-loki3 RT_IDP: IDP_ATTACK_LOG_EVENT: IDP: at 1303673404, ANOMALY Attack log <64.1.2.1/48397->198.87.233.110/80> for TCP protocol and service HTTP application NONE by rule 3 of rulebase IPS in policy Recommended. attack: repeat=0, action=DROP, threat-severity=HIGH, name=HTTP:INVALID:MSNG-HTTP-VER, NAT <46.0.3.254:55870->0.0.0.0:0>, time-elapsed=0, inbytes=0, outbytes=0, inpackets=0, outpackets=0, intf:trust:fe-0/0/2.0->untrust:fe-0/0/3.0, packet-log-id: 0 and misc-message -
# <23> Mar 18 17:56:52 [FW IP] [FW Model]: NetScreen device_id=netscreen2  [Root]system-notification-00257(traffic): start_time="2009-03-18 16:07:06" duration=0 policy_id=320001 service=msrpc Endpoint Mapper(tcp) proto=6 src zone=Null dst zone=self action=Deny sent=0 rcvd=16384 src=21.10.90.125 dst=23.16.1.1
def test_juniper_netscreen_singleport(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} ns204: NetScreen device_id=netscreen2  [Root]system-notification-00257(traffic): start_time=\"2009-03-18 16:07:06\" duration=0 policy_id=320001 service=msrpc Endpoint Mapper(tcp) proto=6 src zone=Null dst zone=self action=Deny sent=0 rcvd=16384 src=21.10.90.125 dst=23.16.1.1\n")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message, host="sc4s-juniper")

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"netscreen:firewall\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1