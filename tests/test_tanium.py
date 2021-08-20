# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment
from pytest import mark

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


def test_tanium_question(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    epoch = epoch[:-7]

    taniumtime = dt.strftime("%Y-%m-%d %H:%M:%S")
    mt = env.from_string(
        '{{ mark }}1 {{ iso }} {{ host }} Tanium 2324 - [tanium_droid@017472 Computer-Name="axo-core-east" IPv4-Address="10.179.79.133" Operating-System="Ubuntu 16.04.6 LTS" Client-Time-UTC="{{ taniumtime }}" IPv6-Address="fe80::ba:bdff:fe75:5845/64" Cloud-Platform="AWS" Cloud-Instance-ID="i-0f680009d715d4ec9" Cloud-Instance-Type="r5a.4xlarge" Cloud-Instance-Location="us-east-1a" Cloud-Instance-Image="ami-0aaaeea4f7f9f8ffd" AWS-Account-ID="063098246926" tanium_droid="sc4s" Question="tanium_droid"] '
    )
    message = mt.render(mark="<14>", iso=iso, host=host, taniumtime=taniumtime)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=epintel host="{{ host }}" sourcetype="tanium"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
