# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import uuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <111>2021-11-25T16:52:18+01:00 SWITCHNAME.domain.com Acl: %ACL-6-IPACCESS: list acl-internet Ethernet1 denied tcp xxx.xx.xx.xx(63751) -> xxx.xx.xx.xx(445)
# <111>2021-11-25T16:52:18+01:00 SWITCHNAME.domain.com Acl: 100: %ACL-6-IPACCESS: list acl-internet Ethernet1 denied tcp xxx.xx.xx.xx(63751) -> xxx.xx.xx.xx(445)
def test_arista_switch(record_property,  setup_splunk, setup_sc4s):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} Acl: %ACL-6-IPACCESS: list acl-internet Ethernet1 denied tcp xxx.xx.xx.xx(63751) -> xxx.xx.xx.xx(445)\n"
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="arista:eos" source="arista:eos:acl" "ACL-6-IPACCESS"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
