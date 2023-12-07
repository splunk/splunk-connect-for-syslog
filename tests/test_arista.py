# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

test_data = [
    {
        "template": "{{ mark }} {{ iso }}Z host {{ program }}: %ACL-6-IPACCESS: list acl-internet Ethernet1 denied tcp xxx.xx.xx.xx(63751) -> xxx.xx.xx.xx(445)",
        "program": "Acl"
    },
    {
        "template": "{{ mark }} {{ iso }}Z {{ program }}: %AGENT-6-INITIALIZED: Agent 'AleL3Agent-primary' initialized; pid=XXXX",
        "program": "AleL3Agent-primary"
    },
    {
        "template": "{{ mark }} {{ iso }}Z {{ program }}: %PROCMGR-6-WORKER_WARMSTART: ProcMgr worker warm start. (PID=XXXXX)",
        "program": "ProcMgr-worker"
    }
]

@pytest.mark.addons("arista")
@pytest.mark.parametrize("event", test_data)
def test_arista_switch(record_property, setup_splunk, setup_sc4s, event):
    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(event["template"] + "\n")
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, program=event["program"])

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype="arista:eos" source="arista:eos:{{ program }}"'
    )
    search = st.render(epoch=epoch, program=event["program"].lower())

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
