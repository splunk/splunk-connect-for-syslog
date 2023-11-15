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

env = Environment(autoescape=select_autoescape(default_for_string=False))


testdata = [
    '{{ mark }}id=firewall sn=C0EFE33057B0 time="{{ delldt }} UTC" fw={{ host }} pri=6 c=1024 m=537 msg="Connection Closed" f=2 n=316039228 src=192.0.0.159:61254:X1: dst=10.0.0.7:53:X3:SIMILDC01 proto=udp/dns sent=59 rcvd=134 vpnpolicy="ELG Main"'
]


@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("dell")
def test_sonicwall_firewall(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    delldt = dt.strftime("%Y-%m-%d %H:%M:%S")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, delldt=delldt)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netfw _time={{ epoch }} sourcetype="dell:sonicwall" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
