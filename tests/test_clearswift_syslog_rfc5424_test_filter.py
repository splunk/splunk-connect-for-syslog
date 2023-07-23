# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import uuid
from jinja2 import Environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment()

# Test Anti Malware
#<22>1 2022-03-28T13:58:27Z AOPRDTETPSEG01 mail - - - postfix-inbound/cleanup[25993]: 4KRvRl1NFRzNhXc3: message-id=<LO0P265MB5503209795971CF16A532CF7EB1D9@LO0P265MB5503.GBRP265.PROD.OUTLOOK.COM>

def test_clearswift(record_property,  setup_splunk, setup_sc4s):
    host = f"test-clearswift-host-{uuid.uuid4().hex}"
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

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1