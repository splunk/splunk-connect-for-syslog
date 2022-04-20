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

# Test Anti Malware
#<22>1 2022-03-28T13:58:27Z AOPRDTETPSEG01 mail - - - postfix-inbound/cleanup[25993]: 4KRvRl1NFRzNhXc3: message-id=<LO0P265MB5503209795971CF16A532CF7EB1D9@LO0P265MB5503.GBRP265.PROD.OUTLOOK.COM>

def test_cisco_ms(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "test-clearswift-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} audit - - - INFO  [Consolidator]- Waiting 2931 milliseconds before processing more log files'
    )
    message = mt.render(mark="<22>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email sourcetype=clearswift* '
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1