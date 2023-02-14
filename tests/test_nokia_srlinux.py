# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest

env = Environment()


# 2023-02-14T18:23:12.620624+00:00 leaf1 sr_chassis_mgr: chassis|1170|1170|00138|W: Interface ethernet-1/1 is now down for reason: port-admin-disabled
# 2023-02-14T18:23:12.620990+00:00 leaf1 sr_xdp_lc_1: debug|1368|1404|00085|W: common    port.cc:2123                      SFlowPortUp  Port ethernet-1/1 - sflow_enabled 1
# 2023-02-14T18:23:18.006002+00:00 leaf1 sr_xdp_lc_1: debug|1368|1402|00002|W: osutils   net_dev.c:365            NetDevPktSockReceive  recvmsg(104, 0x7f1647881eb8, 10240): Network is down (100)
# 2023-02-14T18:23:18.006125+00:00 leaf1 sr_xdp_lc_1: debug|1368|1404|00086|W: common    port.cc:2123                      SFlowPortUp  Port ethernet-1/1 - sflow_enabled 1

testdata = [
 "{{ mark }}{{ iso }} {{ host }} sr_chassis_mgr: chassis|1170|1170|00138|W: Interface ethernet-1/1 is now down for reason: port-admin-disabled",
 "{{ mark }}{{ iso }} {{ host }} sr_xdp_lc_1: debug|1368|1404|00085|W: common    port.cc:2123                      SFlowPortUp  Port ethernet-1/1 - sflow_enabled 1",
]


@pytest.mark.parametrize("event", testdata)
def test_nokia_srlinux(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<366>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="nokia:router" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 2
