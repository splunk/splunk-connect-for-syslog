# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import uuid
import sys

from jinja2 import Environment


from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

@pytest.mark.skipif(sys.platform != 'darwin', reason='it should not run in CICD')
def test_host_override_mk8s(record_property,  setup_splunk, setup_sc4s):
    host = "test_host"
    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string( "{{ mark }}{{ bsd }} {{ host }} Severity: Informational, Category: Audit, MessageID: LOG007, Message: The previous log entry was repeated 0 times.\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="dell:isilion" host="test_host" '
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

