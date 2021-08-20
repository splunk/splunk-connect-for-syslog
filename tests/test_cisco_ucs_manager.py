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

# https://www.ciscolive.com/c/dam/r/ciscolive/us/docs/2017/pdf/TECUCC-3000.pdf

# <190>: 2020 Oct 26 10:33:18 CET: %UCSM-6-AUDIT: [session][internal][creation][internal][3852391][sys/user-ext/web-login-username-web_40207_B][id:web_40207_B, name:username, policyOwner:local][] Web B: remote user username logged in from ipaddr


def test_cisco_ucm_manager(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}: {{ bsd }} {{ tzname }} : %UCSM-6-AUDIT: [session][internal][creation][internal][3852391][sys/user-ext/web-login-username-web_40207_B][id:web_40207_B, name:username, policyOwner:local][] Web B: remote user username logged in from {{ host }}\n"
    )
    message = mt.render(mark="<189>", tzname=tzname, bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops {{ host }} sourcetype="cisco:ucs"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
