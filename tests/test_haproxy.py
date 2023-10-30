# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import shortuuid
import pytz
import pytest

from jinja2 import Environment, select_autoescape, environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


haproxy_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} haproxy[{{ pid }}]: 10.0.0.0:1000 [something]",
]

@pytest.mark.addons("haproxy")
@pytest.mark.parametrize("event", haproxy_testdata)
def test_haproxy(record_property,  setup_splunk, setup_sc4s, get_pid, event):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netlb host={{ host }} sourcetype="haproxy:tcp"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


haproxy_testdata_splunk = [
    r"{{ mark }}{{ bsd }} {{ host }} haproxy[{{ pid }}]: client_ip=10.0.0.0 client_port=1000",
]


@pytest.mark.addons("haproxy")
@pytest.mark.parametrize("event", haproxy_testdata_splunk)
def test_haproxy_splunk(
    record_property,  setup_splunk, setup_sc4s, get_pid, event,
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netlb host={{ host }} sourcetype="haproxy:splunk:http"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
