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

# <13>Jan 18 11:07:53 192.168.1.1 LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# Jan 18 11:07:53 myhostname LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5 cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <13>Jan 18 11:07:53 192.168.1.1 LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
# Jan 18 11:07:53 myhostname LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
testdata1 = [
    "{{ mark }}{{ bsd }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|rc=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ bsd }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
]
testdata2 = [
    "{{ mark }}{{ bsd }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ bsd }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
]
# <13>1 2019-01-18T11:07:53.520Z 192.168.1.1 LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <133>1 2019-01-18T11:07:53.520+07:00 myhostname LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <13>1 2019-01-18T11:07:53.520Z 192.168.1.1 LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
# <133>1 2019-01-18T11:07:53.520+07:00 myhostname LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
@pytest.mark.parametrize("event", testdata1)
def test_leef1_generic(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = iso[0:19] + iso[26:32]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="LEEF:1"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata2)
def test_leef2_generic(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = iso[0:19] + iso[26:32]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="LEEF:2:*"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
