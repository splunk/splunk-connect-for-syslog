# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import random
import sys

from jinja2 import Environment


from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

@pytest.mark.skipif(sys.platform != 'darwin', reason='it should not run in CICD')
def test_custom_ports_mk8s(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} filterlog: 82,,,1000002666,mvneta2,match,pass,out,6,0x00,0x00000,64,ICMPv6,58,8,{{key}},\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6000])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw "{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)
    print(search)
    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

