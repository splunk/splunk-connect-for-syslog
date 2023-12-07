# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


# Apr 15 2017 00:21:14 192.168.12.1: %ACE-3-251010: Health probe failed for server X.X.X.X on port 8000, server reply timeout'
@pytest.mark.addons("cisco")
def test_cisco_ace_traditional(
    record_property,  setup_splunk, setup_sc4s
):
    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} 192.168.12.1: %ACE-3-251010: Health probe failed for server X.X.X.X on port 8000, server reply timeout\n"
    )
    message = mt.render(mark="<111>", bsd=bsd)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype="cisco:ace"'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
