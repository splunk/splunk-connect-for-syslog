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


#
#Mar 25 13:53:24 xxxxxx-xxxx STP: VLAN 125 Port 1/1/24 STP State -> FORWARDING (DOT1wTransition) 
#Mar 25 13:53:25 xxxxx-xxxxx System: PoE: Power disabled on port 1/1/24 because of detection of non-PD. PD detection will be disabled on port. 
#Mar 25 11:50:21 xxxxx-xxxxx Security: SSH terminated by uuuuuuu from src IP 10.1.1.1 from src MAC dddd.dddd.dddd from USER EXEC mode using RSA as Server Host Key. 
testdata = [
    "{{ mark }}{{ bsd }} {{ host }} STP: VLAN 125 Port 1/1/24 STP State -> FORWARDING (DOT1wTransition)",
    "{{ mark }}{{ bsd }} {{ host }} System: PoE: Power disabled on port 1/1/24 because of detection of non-PD. PD detection will be disabled on port.",
    "{{ mark }}{{ bsd }} {{ host }} Security: SSH terminated by uuuuuuu from src IP 10.1.1.1 from src MAC dddd.dddd.dddd from USER EXEC mode using RSA as Server Host Key. ",
]

@pytest.mark.parametrize("event", testdata)
def test_brocade(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = "test_brocade-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"brocade:syslog\" (host=\"{{ host }}\" OR \"{{ host }}\")")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
