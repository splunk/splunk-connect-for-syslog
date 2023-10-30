# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


testdata = [
    "{{ mark }}{{ bsd }} {{ host }}: {{ host }}: 0000001e.0794c163 055b6737 {{ device_time }} [kern_audit:info:2385] 8503ea0000ba6b71 :: nodea:ontapi :: 10.10.10.10:41464 :: nodea-esx:usera :: clone-create :: Error: Missing input: source-path; Missing input: volume",
]


@pytest.mark.addons("netapp")
@pytest.mark.parametrize("event", testdata)
def test_netapp(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    # Wed Jun 23 2021 22:09:18 +10:00
    device_time = dt.strftime("%a %b %d %Y %H:%M:%S +00:00")

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, device_time=device_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="ontap:ems" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
