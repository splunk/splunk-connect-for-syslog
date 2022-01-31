# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <158>Nov 11 15:22:22 xx-09 event: SYSTEM: SYSTEM_CLIENT_CONNECT_FAIL: - - Message VPN (xx) Sol Client username xx clientname xx@RTMD_ALL connect failed from 10.0.0.0:33454 - Forbidden: Client Name Already In Use


def test_solace(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }}{{ host }} event: SYSTEM: SYSTEM_CLIENT_CONNECT_FAIL: - - Message VPN (xx) Sol Client username xx clientname xx@RTMD_ALL connect failed from 10.0.0.0:33454 - Forbidden: Client Name Already In Use\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="solace:eventbroker"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
