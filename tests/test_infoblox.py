# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

#<142>Oct 25 13:08:00 161.231.218.156 named[6597]: FORMERR resolving 'www.google.com/AAAA/IN': 209.2.230.6#53
def test_infoblox_dns(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "vib-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} named[{{ pid }}]: FORMERR resolving 'www.google.com/AAAA/IN': 209.2.230.6#53\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netdns host={{ host }} sourcetype=\"infoblox:dns\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<150>Oct 24 21:09:00 162.101.157.246 dhcpd[28922]: DHCPREQUEST for 10.130.151.62 from 80:ce:62:9c:0e:70 (DTCCE0826E00C97) via eth2 TransID 802c562c uid 01:80:ce:62:9c:0e:70 (RENEW)
def test_infoblox_dhcp(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "vib-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPREQUEST for 10.00.00.62 from 80:00:00:00:0e:70 (EXAMPLE) via eth2 TransID 802c562c uid 01:80:00:00:00:00:70 (RENEW)\n")
    message = mt.render(mark="<150>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netipam host={{ host }} sourcetype=\"infoblox:dhcp\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
