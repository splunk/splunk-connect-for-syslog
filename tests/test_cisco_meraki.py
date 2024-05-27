# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import random

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Log samples from https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Event_Types_and_Log_Samples
mx_test_data = [
    # MX events: vpn connectivity change
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events type=vpn_connectivity_change vpn_type='site-to-site' peer_contact='1.1.1.1:51856' peer_ident='XXXXX' connectivity='false'",
        "host_prefix": "test-mx-",
        "sourcetype": "meraki:securityappliances"
    },
    # urls: HTTP GET requests
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} urls src=1.1.1.1:63735 dst=1.1.1.1:80 mac=XX:XX:XX:XX:XX:XX request: GET https://...",
        "host_prefix": "test-mx-",
        "sourcetype": "meraki:securityappliances"
    },
    # MX flows
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} flows src=1.1.1.186 dst=8.8.8.8 mac=XX:XX:XX:XX:XX:XX protocol=udp sport=55719 dport=53 pattern: allow all",
        "host_prefix": "test-mx-",
        "sourcetype": "meraki:securityappliances"
    },
    # MX firewall
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} firewall src=1.1.1.186 dst=8.8.8.8 mac=XX:XX:XX:XX:XX:XX protocol=udp sport=55719 dport=53 pattern: allow all",
        "host_prefix": "test-mx-",
        "sourcetype": "meraki:securityappliances"
    },
    # MX ids-alerts: ids signature matched
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} ids-alerts signature=129:4:1 priority=3 timestamp=1377449842.512569 direction=ingress protocol=tcp/ip src=1.1.1.1:80",
        "host_prefix": "test-mx-",
        "sourcetype": "meraki:securityappliances"
    }
]

ms_test_data = [
    # MS events: port status change
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events port 3 status changed from 100fdx to down",
        "host_prefix": "test-ms-",
        "sourcetype": "meraki:switches"
    },
    # MS events: blocked DHCP server response
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events Blocked DHCP server response from XX:XX:XX:XX:XX:XX on VLAN 100",
        "host_prefix": "test-ms-",
        "sourcetype": "meraki:switches"
    }
]

mr_test_data = [
    # MR events: 802.11 association
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events type=association radio='0' vap='1' channel='6' rssi='23' aid='XXXXXX'",
        "host_prefix": "test-mr-",
        "sourcetype": "meraki:accesspoints"
    },
    # MR events: WPA authentication
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events type=wpa_auth radio='0' vap='1' aid='XXXXXXX'",
        "host_prefix": "test-mr-",
        "sourcetype": "meraki:accesspoints"
    },
    # MR events: splash authentication
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} events type=splash_auth ip='1.1.1.1 [More Information] ' duration='3600' vap='2' download='5242880bps' upload='5242880bps'",
        "host_prefix": "test-mr-",
        "sourcetype": "meraki:accesspoints"
    },
    # MR flows: flow denied by Layer 3 firewall
    {
        "template": "{{ mark }} {{ epoch }} {{ host }} flows deny src=1.1.1.1 dst=1.1.1.1 mac=XX:XX:XX:XX:XX:XX protocol=tcp sport=52421 dport=80",
        "host_prefix": "test-mr-",
        "sourcetype": "meraki:accesspoints"
    }
]

test_data = mx_test_data + ms_test_data + mr_test_data


@pytest.mark.parametrize("test_case", test_data)
@pytest.mark.addons("cisco")
def test_cisco_meraki_syslog_app(
    record_property, get_host_key, setup_splunk, setup_sc4s, test_case
):
    model_number = random.randint(60, 200)
    model_suffix = random.choice(["", "C", "CW", "W", "-HW", "W-HW"])
    host = f'{test_case["host_prefix"]}{model_number}{model_suffix}'

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    meraki_format_epoch = epoch + "000" # "1691740392.147501" -> "1691740392.147501000"

    mt = env.from_string(test_case["template"] + "\n")
    message = mt.render(mark="<134>", epoch=meraki_format_epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    epoch = dt.astimezone().strftime("%s.%f")[:-3] # -> "1691740392.147501" -> "1691740392.147"
    st = env.from_string(
        'search index=netfw _time={{ epoch }} sourcetype={{ sourcetype }} host={{ host }}'
    )
    search = st.render( epoch=epoch, sourcetype=test_case["sourcetype"], host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <134>1 1563249630.774247467 devicename security_event ids_alerted signature=1:28423:1 priority=1 timestamp=1468531589.810079 dhost=98:5A:EB:E1:81:2F direction=ingress protocol=tcp/ip src=151.101.52.238:80 dst=192.168.128.2:53023 message: EXPLOIT-KIT Multiple exploit kit single digit exe detection
@pytest.mark.addons("cisco")
def test_cisco_meraki_vps_app(
    record_property, setup_splunk, setup_sc4s
):
    host = f"test-meraki-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch_ms = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ epoch }}123 {{ host }} security_event ids_alerted signature=1:28423:1 priority=1 timestamp={{ epoch }} dhost=98:5A:EB:E1:81:2F direction=ingress protocol=tcp/ip src=151.101.52.238:80 dst=192.168.128.2:53023 message: EXPLOIT-KIT Multiple exploit kit single digit exe detection\n"
    )
    message = mt.render(mark="<134>", epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch_ms }} index=netfw host="{{ host }}" sourcetype="meraki"'
    )
    search = st.render(epoch_ms=epoch_ms, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
