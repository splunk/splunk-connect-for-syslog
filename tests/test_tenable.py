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


# <134>May  7 12:39:29 nnm.home.cugnet.net nnm: 192.168.100.1:0|192.168.100.60:0|17|18|Generic Protocol Detection|This plugin determines the IP protocols running on the remote machine.|The remote host is utilizing the following IP protocols :  protocol number 17 (udp) |NONE
testdata = [
    "{{ mark }}{{ bsd }} {{ host }} nnm: 127.0.0.1:0|127.0.0.2:0|17|18|Generic Protocol Detection|This plugin determines the IP protocols running on the remote machine.|The remote host is utilizing the following IP protocols :  protocol number 17 (udp) |NONE",
    "{{ mark }}{{ bsd }} {{ host }} nnm: 127.0.0.3:8080|127.0.0.4:0|6|0|new-open-port|NNM identifies which ports are open or listening on a host. This is detected by observing the response sent from a server or the 'SYN-ACK' sent when receiving a connection.||INFO",
    "{{ mark }}{{ bsd }} {{ host }} nnm: 127.0.0.5:53|127.0.0.6:51329|17|7117|SSL Client Error Code Detection|The client has responded with an SSL error message of : &apos;Close notify &apos; Level : &apos;Warning&apos; Source IP : 192.168.100.1 Dest. IP : 192.168.100.60 |Plugin Output N/A|NONE",
]


@pytest.mark.parametrize("event", testdata)
def test_tenable(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netfw _time={{ epoch }} sourcetype="tenable:nnm:vuln" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
