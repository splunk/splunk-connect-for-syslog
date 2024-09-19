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

testdata = [
    "{{ aruba_time }} {{ host }} tunneld[1234]: CPU 0 TID 0000000000000000: [tunneld.NOTICE]: [cfmst_add_tun] tid 000 type WAN_UDP src 1.2.3.4 dst 4.3.2.1 sport 10 dport 20 proto 0 fmstid 0000000",
    "{{ aruba_time }} {{ host }} tunneld[2222]: CPU 0 TID 0000000000000000: [tunneld.NOTICE]: New license token system max bandwidth 1000000, current=1000000000",
    "{{ aruba_time }} {{ host }} neighd[1111]: CPU 0 TID 0000000000000000: [neighd.NOTICE]: cn_neigh_store_add: 0.0.0.0 aa:aa:25:e0:aa:42 2 : ADDED",
    "{{ aruba_time }} {{ host }} mgmtd[3333]: TID 0000000000000000: [mgmtd.ALERT]: ALARM RAISE: MAJ,EQU,3, equipment_gateway_connect,Next-hop unreachable,gw:0.0.0.0,2022/06/14 23:40:25,1,no,yes,no,yes. Next-Hop Reachability Test Failed",
    "{{ aruba_time }} {{ host }} pm[4444]: TID 0000000000000000: [pm.ALERT]: : Software process ntpd has been restarted"
]


@pytest.mark.addons("aruba")
@pytest.mark.parametrize("event", testdata)
def test_aruba_silverpeak(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "silverpeak-" + get_host_key

    dt = datetime.datetime.now()
    _, _, _, _, _, _, epoch = time_operations(dt)
    aruba_time = dt.strftime("%b %d %H:%M:%S %Y")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(host=host, aruba_time=aruba_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="aruba:silverpeak"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
