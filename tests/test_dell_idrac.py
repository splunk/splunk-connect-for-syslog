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
    "{{ mark }}{{ bsd }} {{ host }} Severity: Informational, Category: Audit, MessageID: LOG007, Message: The previous log entry was repeated 0 times.",
    "{{ mark }}{{ bsd }} {{ host }} Severity: Informational, Category: Audit, MessageID: LOG006, Message: Test event generated for message ID LOG007.",
    "{{ mark }}{{ bsd }} {{ host }} Severity: Informational, Category: Audit, MessageID: USR0032, Message: The session for root from 10.110.161.37 using GUI is logged off.",
    "{{ mark }}{{ bsd }} {{ host }} Severity: Informational, Category: Audit, MessageID: USR0030, Message: Successfully logged in using root, from 10.110.161.37 and GUI.",
]


@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("dell")
def test_dell_idrac(
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
        'search index=infraops _time={{ epoch }} sourcetype="dell:poweredge:idrac:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <134>Feb 18 09:37:41 xxxxxx swlogd: bcmd esm info(5) phy_nlp_enable_set: u=0 p=1 enable:1 phyPresent:YES
cmcdata = [
    "{{ mark }}{{ bsd }} {{ host }} webcgi: session close succeeds: sid=23628",
]


@pytest.mark.parametrize("event", cmcdata)
@pytest.mark.addons("dell")
def test_dell_cmc(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test-dell-cmc-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="dell:poweredge:cmc:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
