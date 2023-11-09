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


#
# Mar 25 13:53:24 xxxxxx-xxxx STP: VLAN 125 Port 1/1/24 STP State -> FORWARDING (DOT1wTransition)
# Mar 25 13:53:25 xxxxx-xxxxx System: PoE: Power disabled on port 1/1/24 because of detection of non-PD. PD detection will be disabled on port.
# Mar 25 11:50:21 xxxxx-xxxxx Security: SSH terminated by uuuuuuu from src IP 10.1.1.1 from src MAC dddd.dddd.dddd from USER EXEC mode using RSA as Server Host Key.
testdata = [
    "{{ mark }}{{ bsd }} {{ host }} ssldata[3934]: [A:81000064] 1450195794 1.2.3.4:49307 -> 5.6.7.8:443 TLS1.0 TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA www.google.com rule:6 resign Success(0x0)",
]

@pytest.mark.addons("broadcom")
@pytest.mark.parametrize("event", testdata)
def test_sslva(
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
        'search index=netproxy _time={{ epoch }} sourcetype="broadcom:sslva" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
