# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random
import pytest
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# Note the long white space is a \t
# Wed May  4 08:42:00 2022        Recordtype=Tunnel Samples       tunneltype=IPSec IKEv2  user=some-one-else@nowhere.com      location=ABC    sourceip=33.22.44.55        destinationip=11.22.33.44     sourceport=0    txbytes=2595428 rxbytes=0       dpdrec=0        vendor=Zscaler        product=tunnel_sample
def test_zscaler_tunnel(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ date }} {{ time }}\tRecordtype=Tunnel Samples\ttunneltype=IPSec\tuser=some-one-else@nowhere.com\tlocation=ABC\tsourceip=33.22.44.55\tdestinationip=11.22.33.4\tsourceport=0\ttxbytes=2595428\tserverip=192.168.0.1\tdpdrec=0\tvendor=Zscaler\tproduct=IKEv2\thost={{ host }}"
    )
    message = mt.render(mark="<134>", date=date, time=time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype="zscalernss-tunnel" '
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


