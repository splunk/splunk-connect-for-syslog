# Copyright 2024 Splunk, Inc.
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

env = Environment(autoescape=select_autoescape(default_for_string=False))

# System log messages
#<165>1 2023-12-15T10:39:54.732530-05:00 TW0T0RMVXXXXXXXXXXXX bgp#zebra 292 - -  message repeated 101 times: [ [XXXXX-XXXXX][EC XXXXXXXXX] snmp[err]: truncating integer value > 32 bits]

testdata = [
    "{{ mark }}1 {{ timestamp }} {{ host }} bgp#zebra 292 - -  message repeated 101 times: [ [XXXXX-XXXXXD][EC XXXXXXXXX] snmp[err]: truncating integer value > 32 bits]",
]


@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("dell")
def test_sonic(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = 'sonic-' + get_host_key # example parser package/etc/test_parsers/app-vps-dell_switch_n.conf filters on host value

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)
    delldt = dt.strftime("%Y-%m-%d %H:%M:%S")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", timestamp=delldt, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="dell:sonic" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
