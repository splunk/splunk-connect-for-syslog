# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest

env = Environment()


testdata = [
    '{{ mark }}id=firewall sn=C0EFE33057B0 time="{{ delldt }} UTC" fw={{ host }} pri=6 c=1024 m=537 msg="Connection Closed" f=2 n=316039228 src=192.0.0.159:61254:X1: dst=10.0.0.7:53:X3:SIMILDC01 proto=udp/dns sent=59 rcvd=134 vpnpolicy="ELG Main"'
]


@pytest.mark.parametrize("event", testdata)
def test_sonicwall_firewall(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    delldt = dt.strftime("%Y-%m-%d %H:%M:%S")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, delldt=delldt)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netfw _time={{ epoch }} sourcetype="dell:sonicwall:firewall:firewall" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
