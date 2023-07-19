# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import uuid

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


def test_netscout_arboredge(record_property,  setup_splunk, setup_sc4s):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    epochlong = int(epoch) * 1000

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CEF:0|NETSCOUT|Arbor Edge Defense|6.8.1.0|TCP Connection Limiting|Blocked Host|5|rt={{ epochlong }} src=190.0.0.0 dpt=25 cn2=109 proto=TCP dst=8.8.8.8 spt=8477 cs2Label=Protection Group Name cn2Label=Protection Group ID cs2=Test_MAIL\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, epochlong=epochlong)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="netscout:aed"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
