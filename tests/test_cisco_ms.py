# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <11>Jan 16 04:25:44 user.info cms20 authp:  Using authentication server cb_video.cms20.video.uc.lab to authenticate user tyamada@cms20.video.uc.lab (index: 1/1, reason: first match)

@pytest.mark.addons("cisco")
def test_cisco_ms(record_property,  setup_splunk, setup_sc4s):
    host = f"test-cms-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} user.info {{ host }} authp:  Using authentication server cb_video.cms20.video.uc.lab to authenticate user tyamada@cms20.video.uc.lab (index: 1/1, reason: first match)\n"
    )
    message = mt.render(mark="<189>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:ms"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
