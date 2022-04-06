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
#486 <132>1 2022-04-05T19:56:42.387000Z Barracuda - - - src=10.1.1.1 spt=33217 dst=10.1.1.1 dpt=39971 actionTaken=DENY attackDescription=GEO_IP_BLOCK attackDetails=GeoIP Policy Match attackGroup=Forceful Browsing attackId=1111 logType=WF app=TLSv1.2 request=/apps/ requestMethod=GET rt=1649197620642 userAgent=Mozilla/5.0 [en] (X11, U; OpenVAS-VT 9.0.3) referer=
def test_barracuda(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} Barracuda - - - src=10.1.1.1 spt=33217 dst=10.1.1.1 dpt=39971 actionTaken=DENY attackDescription=GEO_IP_BLOCK attackDetails=GeoIP Policy Match attackGroup=Forceful Browsing attackId=1111 logType=WF app=TLSv1.2 request=/apps/ requestMethod=GET rt=1649197620642 userAgent=Mozilla/5.0 [en] (X11, U; OpenVAS-VT 9.0.3) referer='
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netwaf  sourcetype="barracuda:wf"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
