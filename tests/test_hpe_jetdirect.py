# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import datetime

import pytest
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


# <134> printer: Device Administrator Password modified; time="2015-Apr-09 11:54 AM (UTC-07:00)" user="admin" source_IP="10.0.0.7" outcome=success interface=Wired
testdata = [
    r'{{ mark }} printer: Device Administrator Password modified; time="{{ hptime }} (UTC-00:00)" user="admin" source_IP="{{ host}}" outcome=success interface=Wired',
    r'{{ mark }} scanner: Device Administrator Password modified; time="{{ hptime }} (UTC-00:00)" user="admin" source_IP="{{ host}}" outcome=success interface=Wired',
]


@pytest.mark.parametrize("event", testdata)
def test_hpe_jetdirect(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)

    print(dt)
    hptime = dt.strftime("%Y-%b-%d %I:%M %p")
    print(hptime)
    epoch = dt.astimezone().strftime("%s")
    print(epoch)
    tt = dt.strptime(hptime + "-0000", "%Y-%b-%d %I:%M %p%z")
    print(tt)
    ttepoch = tt.astimezone().strftime("%s")
    print(ttepoch)

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>", host=host, hptime=hptime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=print "{{ host }}" sourcetype="hpe:jetdirect"'
    )
    search = st.render(epoch=ttepoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
