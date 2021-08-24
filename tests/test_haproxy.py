# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random

import pytest
import pytz
from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


haproxy_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} haproxy[{{ pid }}]: 10.0.0.0:1000 [something]",
]


@pytest.mark.parametrize("event", haproxy_testdata)
def test_haproxy(record_property, setup_wordlist, setup_splunk, setup_sc4s, event):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netlb host={{ host }} sourcetype="haproxy:tcp"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


haproxy_testdata_splunk = [
    r"{{ mark }}{{ bsd }} {{ host }} haproxy[{{ pid }}]: client_ip=10.0.0.0 client_port=1000",
]


@pytest.mark.parametrize("event", haproxy_testdata_splunk)
def test_haproxy_splunk(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netlb host={{ host }} sourcetype="haproxy:splunk:http"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
