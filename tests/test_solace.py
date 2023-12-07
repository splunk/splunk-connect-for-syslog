# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <158>Nov 11 15:22:22 xx-09 event: SYSTEM: SYSTEM_CLIENT_CONNECT_FAIL: - - Message VPN (xx) Sol Client username xx clientname xx@RTMD_ALL connect failed from 10.0.0.0:33454 - Forbidden: Client Name Already In Use

testdata = [
    "{{ mark }}{{ bsd }}{{ host }} event: SYSTEM: SYSTEM_CLIENT_CONNECT_FAIL: - - Message VPN (xx) Sol Client username xx clientname xx@RTMD_ALL connect failed from 10.0.0.0:33454 - Forbidden: Client Name Already In Use"
    "{{ mark }}{{ bsd }}{{ host }} event: CLIENT: CLIENT_CLIENT_OPEN_FLOW: mvpn_sdi3cnc SESS-XA_TMS_ALM-CFG Client (8181) SESS-XA_TMS_ALM-CFG username cuid_sdi3cnc_tmalpha Pub flow session flow name 241defac2d4140c2ad00647e848963ed (7270), transacted session id -1, publisher id 9470, last message id 0, window size 10"
    "{{ mark }}{{ bsd }}{{ host }} event: VPN: VPN_AD_MSG_SPOOL_HIGH_CLEAR: mvpn_sdi3 - Message VPN (4) Queue QUE_FEEDS-P1_LOGV message spool threshold 18432 kB (18%) cleared: 18418 kB"
]


@pytest.mark.parametrize("event", testdata)
@pytest.mark.addons("solace")
def test_solace(record_property,  setup_splunk, setup_sc4s, event):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="solace:eventbroker"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
