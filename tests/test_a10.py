# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
import random
from .timeutils import *

env = Environment()

def test_a10_vthunder(
    record_property, setup_splunk, setup_sc4s
):
    mt = env.from_string(
       "{{ mark }} CEF:0|A10|vThunder|4.1.4-GR1-P12|WAF|session-id|2|rt={{ bsd }} src=1.1.1.1 spt=34860 dst=1.1.1.1 dpt=80 dhost=test.host.local cs1=uiext_sec_waf cs2=1 act=learn cs3=learn app=HTTP requestMethod=GET cn1=0 request=/sales/ msg=New session created: Id\=1\n"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=dt.strftime("%b %d %Y %H:%M:%S"))

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netwaf sourcetype="a10networks:vThunder:cef" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1