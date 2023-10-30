# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

testdata = [
    "{{mark}}{{ bsd }} {{ host }} forward: in:ether1 out:bridge, src-mac 26:5a:4c:57:6e:cc, proto TCP (SYN), 192.168.1.196:62583->10.1.0.0:8000, len 64",
]
# Tue, 15 Jun 2021 02:35:28 +1000


@pytest.mark.addons("mikrotik")
@pytest.mark.parametrize("event", testdata)
def test_routeros(record_property,  setup_splunk, setup_sc4s, event):
    host = f"test-mrtros-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]
    device_time = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<132>", bsd=bsd, host=host, device_time=device_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search index=netfw _time={{ epoch }} sourcetype="routeros"')

    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
