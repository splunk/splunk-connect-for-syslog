# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid
import sys

from jinja2 import Environment, select_autoescape


from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

@pytest.mark.skipif(sys.platform != 'darwin', reason='it should not run in CICD')
def test_custom_ports_mk8s(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

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
    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

