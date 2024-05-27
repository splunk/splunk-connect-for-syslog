# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <134> printer: Device Administrator Password modified; time="2015-Apr-09 11:54 AM (UTC-07:00)" user="admin" source_IP="10.0.0.7" outcome=success interface=Wired
testdata = [
    r'{{ mark }} printer: Device Administrator Password modified; time="{{ hptime }} (UTC-00:00)" user="admin" source_IP="{{ host}}" outcome=success interface=Wired',
    r'{{ mark }} scanner: Device Administrator Password modified; time="{{ hptime }} (UTC-00:00)" user="admin" source_IP="{{ host}}" outcome=success interface=Wired',
]


@pytest.mark.addons("hp")
@pytest.mark.parametrize("event", testdata)
def test_hpe_jetdirect(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
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

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
