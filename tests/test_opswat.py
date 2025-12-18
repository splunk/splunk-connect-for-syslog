# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("opswat")
def test_opswat(
    record_property, setup_splunk, setup_sc4s, get_host_key
):
    host = get_host_key
    mt = env.from_string(
       "{{ mark }}{{ bsd }} {{ host }} OPSWATPC CEF:0|OPSWAT|MSCL|4.16.0|core.network|MSCL[7548] New maximum agent count is set|2|maxAgentCount='1' msgid=665"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<134>", bsd=bsd, host=host)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    
    st = env.from_string(
        'search index=netwaf sourcetype="opswat:mscl:cef" earliest={{ epoch }}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1