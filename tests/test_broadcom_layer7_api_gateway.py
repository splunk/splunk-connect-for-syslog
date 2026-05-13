# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import datetime

import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Reconstructed from a Splunk screenshot: RFC3164 header + java.util.logging traffic line.
# The trailing payload after `com.l7tech.traffic:` is controlled by the gateway cluster
# property `trafficlogger.detail` and is fully customer-configurable, so this test only
# verifies that the message is classified to the broadcom:layer7_api_gateway sourcetype;
# it does not assert any field-level extraction.
layer7_traffic_samples = [
    r"{{ mark }}{{ bsd }} {{ host }} SSG[{{ pid }}]: INFO com.l7tech.traffic: 2025-02-21T19:58:47.968Z; ; ; ; 200; 158; KOU4U2RNQ1; GET; intg.api.ia.ca; /omni/promotions/v2/contests/DIGITAL_ADOPTION_CLIENT_2025/participants/self; https://we.INTG.webservice.ia.iafg.net/WEMWPNA4/v2/contests/DIGITAL_ADOPTION_CLIENT_2025/participants/self; 87; 200",
]


@pytest.mark.addons("broadcom")
@pytest.mark.parametrize("event", layer7_traffic_samples)
def test_broadcom_layer7_api_gateway_traffic(
    record_property, get_host_key, get_pid, setup_splunk, setup_sc4s, event
):
    host = get_host_key
    pid = get_pid

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<134>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="broadcom:layer7_api_gateway" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
