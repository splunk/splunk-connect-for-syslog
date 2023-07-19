# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import uuid

from jinja2 import Environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment()


# Apr 15 2017 00:21:14 192.168.12.1: %ACE-3-251010: Health probe failed for server X.X.X.X on port 8000, server reply timeout'
def test_cisco_ace_traditional(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }}: %ACE-3-251010: Health probe failed for server X.X.X.X on port 8000, server reply timeout\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ace"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
