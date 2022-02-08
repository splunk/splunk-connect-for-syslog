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

# <11>Jan 16 04:25:44 user.info cms20 authp:  Using authentication server cb_video.cms20.video.uc.lab to authenticate user tyamada@cms20.video.uc.lab (index: 1/1, reason: first match)


def test_cisco_cmc(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "test-ccmc-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} user.info {{ host }} authp:  Using authentication server cb_video.cms20.video.uc.lab to authenticate user tyamada@cms20.video.uc.lab (index: 1/1, reason: first match)\n"
    )
    message = mt.render(mark="<189>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:cmc"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
