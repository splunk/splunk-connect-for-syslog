# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Note the long white space is a \t
# Wed May  4 08:42:00 2022        Recordtype=Tunnel Samples       tunneltype=IPSec IKEv2  user=some-one-else@nowhere.com      location=ABC    sourceip=33.22.44.55        destinationip=11.22.33.44     sourceport=0    txbytes=2595428 rxbytes=0       dpdrec=0        vendor=Zscaler        product=tunnel_sample
@pytest.mark.addons("zscaler")
def test_zscaler_tunnel(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, time, date, _, _, epoch = time_operations(dt)

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

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


