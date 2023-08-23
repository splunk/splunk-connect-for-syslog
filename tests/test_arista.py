# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

test_data = [
    "{{ mark }} {{ iso }}Z host Acl: %ACL-6-IPACCESS: list acl-internet Ethernet1 denied tcp xxx.xx.xx.xx(63751) -> xxx.xx.xx.xx(445)",
    "{{ mark }} {{ iso }}Z AleL3Agent-primary: %AGENT-6-INITIALIZED: Agent 'AleL3Agent-primary' initialized; pid=XXXX",
    "{{ mark }} {{ iso }}Z ProcMgr-worker: %PROCMGR-6-WORKER_WARMSTART: ProcMgr worker warm start. (PID=XXXXX)"
]


@pytest.mark.parametrize("event", test_data)
def test_arista_switch(record_property, setup_wordlist, setup_splunk, setup_sc4s, event):

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype="arista:eos" source="arista:eos:acl" "ACL-6-IPACCESS"'
    )
    search = st.render(epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
