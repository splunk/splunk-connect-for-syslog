# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *
import pytest

env = Environment()

testdata = [
    "{{mark}}{{ bsd }} {{ host }} forward: in:ether1 out:bridge, src-mac 26:5a:4c:57:6e:cc, proto TCP (SYN), 192.168.1.196:62583->10.1.0.0:8000, len 64",
]
# Tue, 15 Jun 2021 02:35:28 +1000


@pytest.mark.parametrize("event", testdata)
def test_routeros(record_property, setup_wordlist, setup_splunk, setup_sc4s, event):
    host = "test-mrtros-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]
    device_time = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<132>", bsd=bsd, host=host, device_time=device_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search index=netfw _time={{ epoch }} sourcetype="routeros"')

    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
