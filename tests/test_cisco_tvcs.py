# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()
# <166>2018-06-27T12:17:46Z asa : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
def test_cisco_tvcs_rfc5424(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }}Z {{ host }} tvcs: tvcs: UTCTime="2020-11-18 19:55:58,980" Module="network.sip" Level="INFO":  Action="Received" Local-ip="10.101.34.204" Local-port="26999" Src-ip="10.109.41.206" Src-port="5060" Detail="Receive Response Code=100, Method=REGISTER, CSeq=2113, To=sip:+15558121064@xxx-CMSUB-16P.xxxx.org, Call-ID=38ed18ae-4e3c0023-15d22215-5d1c0b88@192.168.1.4, From-Tag=38ed18ae4e3c072f02842674-263fafe9, To-Tag=, Msg-Hash=12083697096016829312, Local-SessionID=, Remote-SessionID="\n'
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="cisco:tvcs"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
