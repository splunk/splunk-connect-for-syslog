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


# <134>Feb 18 09:37:41 xxxxxx swlogd: bcmd esm info(5) phy_nlp_enable_set: u=0 p=1 enable:1 phyPresent:YES
testdata = [
    "{{ mark }}{{ bsd }} {{ host }} BG[123]: 1427:01:01:event=logout;site=support.xxx.xxx.gov;target=rep_client;when=1643824736;who=unknown (asdf) using password;who_ip=10.0.85.35",
]


@pytest.mark.addons("beyondtrust")
@pytest.mark.parametrize("event", testdata)
def test_beyondtrust_sra(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="beyondtrust:sra" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("beyondtrust")
def test_beyondtrust_parts(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    event = "{{ mark }}{{ bsd }} {{ host }} BG[123]: 1427:01:02:event=logout;site=support.xxx.xxx.gov;target=rep_client;when=1643824736;who=unknown (asdf) using password;who_ip=10.0.85.35"
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    event = "{{ mark }}{{ bsd }} {{ host }} BG[123]: 1427:02:02:foo=bar;this=that"
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="beyondtrust:sra" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
