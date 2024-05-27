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
    '{{ mark }}{{ bsd }} {{ host }} Core: @@306,apChannelChanged,"apMac"="54:EC:2F:35:99:50","radio"="11g/n","fromChannel"="1","toChannel"="6","apName"="65-xx-xx-05labo.example.com","fwVersion"="5.2.2.0.1016","model"="R610","zoneUUID"="a7caf05c-3af6-4015-a715-5fc2aa0c16cf","zoneName"="Institut_Pasteur","timeZone"="CET-1CEST,M3.4.0/01:00,M10.5.0/01:00","apLocation"="","apGps"="","apIpAddress"="10.1.1.1","apIpv6Address"="","apGroupUUID"="34af29ac-1adb-4300-b851-d42b6ac555c3","domainId"="8b2081d5-9662-40d9-a3db-2a3cf4dde3f7","serialNumber"="401949001011","domainName"="Administration Domain","idealEventVersion"="3.5.1","apDescription"=""',
]

@pytest.mark.addons("ruckus")
@pytest.mark.parametrize("event", testdata)
def test_rukus_smartzone(
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
        'search index=netops _time={{ epoch }} sourcetype="ruckus:smartzone" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
