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


@pytest.mark.addons("liveaction")
def test_liveaction_livenx_event(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }}2022-01-17T13:15:08+00:00  %LIVEACTION: Device={{ host }} Class=Queue0, Interface Direction=Output, Initial BitRate=0.00 Kbps, Latest BitRate=0.00 Kbps, Configured Threshold=0.00 Kbps, Policy=AAA_BBB_CCC_DDD, Tag(s)=vpn0'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<132>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops sourcetype="liveaction:livenx" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
