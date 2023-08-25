# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


# Apr 15 2017 00:21:14 192.168.12.1: %ACE-3-251010: Health probe failed for server X.X.X.X on port 8000, server reply timeout'
def test_cisco_ace_traditional(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
