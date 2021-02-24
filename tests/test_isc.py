# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz
import pytest

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


isc_dns_testdata = [
    r'{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: Recursion cache view "_default": size = 89496, hits = 1, misses = 3',
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.205 client 192.168.1.3#61567: UDP: query: 2.1.168.192.in-addr.arpa IN PTR response: NXDOMAIN +",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.329 client 192.168.1.3#61568: UDP: query: abc.com IN A response: NOERROR + abc.com. 60 IN A 13.32.86.14; abc.com. 60 IN A 13.32.86.89; abc.com. 60 IN A 13.32.86.7; abc.com. 60 IN A 13.32.86.42;",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.336 client 192.168.1.3#61569: UDP: query: abc.com IN AAAA response: NOERROR +",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c74087120 192.168.1.3#61568 (abc.com): query: abc.com IN A + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61567 (2.1.168.192.in-addr.arpa): query: 2.1.168.192.in-addr.arpa IN PTR + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61567 (2.1.168.192.in-addr.arpa): RFC 1918 response from Internet for 2.1.168.192.in-addr.arpa",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61569 (abc.com): query: abc.com IN AAAA + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: FORMERR resolving 'www.google.com/AAAA/IN': 209.2.230.6#53",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: Recursion client quota: used/max/soft-limit/s-over/hard-limit/h-over/low-pri = 0/1/900/0/1000/0/0",
]

isc_dhcp_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: Abandoning IP address 192.168.1.125: pinged before offer",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPACK on 192.168.1.120 to 00:50:56:13:60:56 (dummyhost) via eth1 relay eth1 lease-duration 600 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPDISCOVER from 00:50:56:13:60:56 via eth1 TransID c02c6bb8 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPEXPIRE on 192.168.1.125 to 00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPOFFER on 192.168.1.120 to 00:50:56:13:60:56 (dummyhost) via eth1 relay eth1 lease-duration 119 offered-duration 600 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPRELEASE of 192.168.1.126 from 00:50:56:13:60:56 (dummyhost) via eth1 (found) TransID 8554a358 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPREQUEST for 10.130.151.62 from 80:ce:62:9c:0e:70 (DTCCE0826E00C97) via eth2 TransID 802c562c uid 01:80:ce:62:9c:0e:70 (RENEW)",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPREQUEST for 192.168.1.120 (192.168.1.2) from 00:50:56:13:60:56 (dummyhost) via eth1 TransID 9a5fbd6e uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: uid lease 192.168.1.125 for client 00:50:56:13:60:56 is duplicate on 192.168.1.0/24",
]

# @pytest.mark.parametrize("event", isc_dns_testdata)
# def test_isc_dns(record_property, setup_wordlist, setup_splunk, setup_sc4s, event):
#     host = "infoblox-{}-{}".format(
#         random.choice(setup_wordlist), random.choice(setup_wordlist)
#     )
#     pid = random.randint(1000, 32000)

#     dt = datetime.datetime.now()
#     iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

#     # Tune time functions
#     epoch = epoch[:-7]

#     mt = env.from_string(event + "\n")
#     message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

#     sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

#     st = env.from_string(
#         'search _time={{ epoch }} index=netdns host={{ host }} sourcetype="infoblox:dns"'
#     )
#     search = st.render(epoch=epoch, host=host)

#     resultCount, eventCount = splunk_single(setup_splunk, search)

#     record_property("host", host)
#     record_property("resultCount", resultCount)
#     record_property("message", message)

#     assert resultCount == 1


@pytest.mark.parametrize("event", isc_dhcp_testdata)
def test_isc_dhcp(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<150>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netipam host={{ host }} sourcetype="isc:dhcp"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

