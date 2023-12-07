# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <27>Mar 24 21:45:28 10.1.1.1 Detected an unauthorized user attempting to access the SNMP interface from 10.1.1.1 0x0004
@pytest.mark.addons("schneider")
def test_apc(record_property,  setup_splunk, setup_sc4s):
    host = f"test_apc-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} {{ host }} Detected an unauthorized user attempting to access the SNMP interface from 10.1.1.1 0x0004\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main sourcetype=apc:syslog host="{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
