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


def test_pulse_secure_5424(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} PulseSecure: - - - ive | 2020-09-16 18:10:53 | ADM100 | info | 10.251.0.1 |  | 172.30.0.21 | username | Ace Admin |  |  |  |  |  |  | Admin user 'username' has accepted Pulse EULA\n"
    )
    message = mt.render(mark="<14>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pulse:connectsecure"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_pulse_secure_6587(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} PulseSecure: - - - ive | 2020-09-16 18:10:53 | ADM100 | info | 10.251.0.1 |  | 172.30.0.21 | username | Ace Admin |  |  |  |  |  |  | Admin user 'username' has accepted Pulse EULA"
    )
    message = mt.render(mark="<14>", iso=iso, host=host)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pulse:connectsecure"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

