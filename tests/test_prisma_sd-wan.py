# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment
import random

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
import datetime

import pytest

env = Environment()

def generate_random_ipv4():
    random_octet = lambda: format(random.randint(0, 255))
    return ".".join([random_octet() for _ in range(4)])


# Prisma SD-WAN ION flow information
# <13>1 2023-09-26T23:28:26.000035+00:00 MYDEVICENAME cgxFlowLogV1 20681 - - 2023-09-26T23:28:26,10.10.10.64,52172,208.67.222.222,443,udp,,,1,1,224,490,,ISP1,,,Delete flow (udp flow timeout),
# <13>1 2023-09-26T23:28:26.000035+00:00 MYDEVICENAME cgxFlowLogV1 20681 - - 2023-09-26T23:28:26,10.10.10.52,62353,10.10.12.55,135,tcp,,,8,6,672,896,,ISP1,,msrpc-base,Delete flow (tcp closed by FIN or RST),
# <13>1 2020-01-28T23:46:17.000035+00:00 MYDEVICENAME cgxFlowLogV1 13593 - - 2020-01-28T23:46:17,10.2.53.102,52520,10.2.13.100,80,tcp,,,0,0,0,0,,LondonPriWI1,15796434157670062,enterprise-http,New Flow,Allow-All:allow:1
flow_logs = [
    "{{ mark }}1 {{ timestamp }} {{ host }} cgxFlowLogV1 20681 - - 2023-09-26T23:28:26,10.10.10.64,52172,208.67.222.222,443,udp,,,1,1,224,490,,ISP1,,,Delete flow (udp flow timeout),",
    "{{ mark }}1 {{ timestamp }} {{ host }} cgxFlowLogV1 20681 - - 2023-09-26T23:28:26,10.10.10.52,62353,10.10.12.55,135,tcp,,,8,6,672,896,,ISP1,,msrpc-base,Delete flow (tcp closed by FIN or RST)",
    "{{ mark }}1 {{ timestamp }} {{ host }} cgxFlowLogV1 13593 - - 2020-01-28T23:46:17,10.2.53.102,52520,10.2.13.100,80,tcp,,,0,0,0,0,,LondonPriWI1,15796434157670062,enterprise-http,New Flow,Allow-All:allow:1"
]

@pytest.mark.addons("paloalto")
@pytest.mark.parametrize("event", flow_logs)
def test_prisma_flow_logs(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    epoch = dt.astimezone().strftime("%s.%f")[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", timestamp=formatted_date, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="prisma:sd-wan:flow" host={{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Prisma SD-WAN ION authentication logs:
# <11>1 2023-09-26T23:36:36.882Z 10.10.10.51 log - - -  ION_HOST="MYDEVICENAME" DEVICE_TIME="2023-09-26T23:36:36.882Z" MSG="sshd-all:error: Received disconnect from 10.10.200.95 port 51711:14: Unable to authenticate using any of the configured authentication methods.  [preauth]" SEVERITY="major" PROCESS_NAME="sshd" FACILITY="auth" ELEMENT_ID="1689170211556024796"
# <11>1 Feb 14 10:44:58 172.20.75.186 log: ION_HOST="ion7k-Hub" DEVICE_TIME="2018-02-14T10:44:58.881Z" MSG="sshd-login keyboard-interactive/pam" SEVERITY="minor" PROCESS_NAME="sshd" FACILITY="auth" USER="elem-admin" ELEMENT_ID="15174644824510129"
authentication_logs = [
    '{{ mark }}1 {{ timestamp }} {{ host }} log - - -  ION_HOST="MYDEVICENAME" DEVICE_TIME="2023-09-26T23:36:36.882Z" MSG="sshd-all:error: Received disconnect from 10.10.200.95 port 51711:14: Unable to authenticate using any of the configured authentication methods.  [preauth]" SEVERITY="major" PROCESS_NAME="sshd" FACILITY="auth" ELEMENT_ID="1689170211556024796"',
    '{{ mark }}1 {{ timestamp }} {{ host }} log: ION_HOST="ion7k-Hub" DEVICE_TIME="2018-02-14T10:44:58.881Z" MSG="sshd-login keyboard-interactive/pam" SEVERITY="minor" PROCESS_NAME="sshd" FACILITY="auth" USER="elem-admin" ELEMENT_ID="15174644824510129"'
]

@pytest.mark.addons("paloalto")
@pytest.mark.parametrize("event", authentication_logs)
def test_prisma_authentication_logs(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = generate_random_ipv4()

    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    epoch = dt.astimezone().strftime("%s.%f")[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<11>", timestamp=formatted_date, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="prisma:sd-wan:authentication" host={{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Prisma SD-WAN ION event logs (in response to alerts and alarms):
# <10>1 2023-10-04T16:20:15.687Z 10.10.10.51 alarm - - - ION_HOST="MyDevice1" DEVICE_TIME="2023-10-04T16:20:15.687Z" STATUS="cleared" CODE="DEVICESW_CONCURRENT_FLOWLIMIT_EXCEEDED" Severity="critical" CONCURRENT_LIMIT="100000" IDENTIFIER="1689170154632020296" ELEMENT_ID="1689170211556024796"
# <11>1 2023-10-04T16:45:15.608Z 10.10.10.203 alarm - - - ION_HOST="MyDevice22" DEVICE_TIME="2023-10-04T16:45:15.608Z" STATUS="Not clear" CODE="NETWORK_VPNLINK_DOWN" Severity="major" AL_ID="1692211457478015096" VPN_LINK_ID="1693496601376017896" IDENTIFIER="1693496601376017596" ELEMENT_ID="1690471915306003396"
event_logs = [
    '{{ mark }}1 {{ timestamp }} {{ host }} alarm - - - ION_HOST="MyDevice1" DEVICE_TIME="2023-10-04T16:20:15.687Z" STATUS="cleared" CODE="DEVICESW_CONCURRENT_FLOWLIMIT_EXCEEDED" Severity="critical" CONCURRENT_LIMIT="100000" IDENTIFIER="1689170154632020296" ELEMENT_ID="1689170211556024796"',
    '{{ mark }}1 {{ timestamp }} {{ host }} alarm - - - ION_HOST="MyDevice22" DEVICE_TIME="2023-10-04T16:45:15.608Z" STATUS="Not clear" CODE="NETWORK_VPNLINK_DOWN" Severity="major" AL_ID="1692211457478015096" VPN_LINK_ID="1693496601376017896" IDENTIFIER="1693496601376017596" ELEMENT_ID="1690471915306003396"'
]

@pytest.mark.addons("paloalto")
@pytest.mark.parametrize("event", event_logs)
def test_prisma_event_logs(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = generate_random_ipv4()

    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    epoch = dt.astimezone().strftime("%s.%f")[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<10>", timestamp=formatted_date, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="prisma:sd-wan:event" host={{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1