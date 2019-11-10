# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])
#<27>Nov  8 17:28:43 US8P60,18e8294876c3,v4.0.66.10832 switch: DOT1S: dot1sBpduReceive(): Discarding the BPDU on port 0/7, since it is an invalid BPDU type

def test_ubiquiti_unifi(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{mark}}{% now 'utc', '%b %d %H:%M:%S' %} US8P60,18e8294876c3,v4.0.66.10832 switch: DOT1S: dot1sBpduReceive(): Discarding the BPDU on port 0/7, since it is an invalid BPDU type")
    message = mt.render(mark="<27>", host=host)
    sendsingle(message)

    st = env.from_string("search index=netops sourcetype=ubnt earliest=-2m | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1