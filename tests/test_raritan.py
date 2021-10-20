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

# <110>M_00796:  User radware Session with client radware was terminated due to Inactivity.
def test_raritan_dsx(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}[Login Failed]: Authentication failed for user 'cartertest' from host '{{ key }}'\n"
    )
    message = mt.render(mark="<27>", key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9001])

    st = env.from_string('search index=infraops sourcetype=raritan:dsx "{{key}}"')
    search = st.render(epoch=epoch, key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
