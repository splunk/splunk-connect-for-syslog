# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
import datetime

import pytest
import random

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <111> Jan 22 20:01:41 10.x.x.x 22 Jan 2024 20:01:41 host1 Radius UserID=abc@company.com AD Password Accepted From ClientIP=10.x.x.x RemoteID= Passcode Check Still Required
# <111> Jan 22 19:52:51 10.x.x.x 22 Jan 2024 19:52:51 host2 Radius UserID=dag@cmy.com Passcode OK Access Accepted with Soft Token From ClientIP=10.x.y.z RemoteID=
testdata = [
    "{{ mark }} {{ timestamp }} {{ host }} {{ timestamp }} host1 Radius UserID=abc@company.com AD Password Accepted From ClientIP=10.x.x.x RemoteID= Passcode Check Still Required",
    "{{ mark }} {{ timestamp }} {{ host }} {{ timestamp }} host2 Radius UserID=dag@cmy.com Passcode OK Access Accepted with Soft Token From ClientIP=10.x.y.z RemoteID="
]

@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("securenvoy")
def test_securenvoy(record_property,  setup_splunk, setup_sc4s, event):
    host = ".".join([str(random.randint(0, 255)) for _ in range(4)]) # random IPv4

    dt = datetime.datetime.now()
    securenvoy_timestamp = dt.strftime("%b %d %H:%M:%S")
    epoch = dt.astimezone().strftime("%s.%f")[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", timestamp=securenvoy_timestamp, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="securenvoy"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
