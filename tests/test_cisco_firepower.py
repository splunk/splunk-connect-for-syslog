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


# Apr 15 2017 00:22:42 192.168.12.1 : %FWSM-6-106100: access-list outside-access-in ##permission## ##transport## outside/XXX.XXX.XXX.XXX(##port_1##) -> inside/XXX.XXX.XXX.XXX(9997) hit-cnt 1 (first hit) [0xe0ba389d, 0x0]
def test_cisco_firepower(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} SFIMS: Protocol: TCP, SrcIP: 1.1.1.1, OriginalClientIP: ::, DstIP: 2.2.2.2, SrcPort: 47097, DstPort: 33897, TCPFlags: 0x0, DE: Primary Detection Engine (asdf912a-ad91-d192-adsf-12aadf32910d), Policy: device-policy, ConnectType: Start, AccessControlRuleName: EU-NoLicense-Block-All, AccessControlRuleAction: Block with reset, Prefilter Policy: Default Prefilter Policy, InitiatorPackets: 1, ResponderPackets: 0, InitiatorBytes: 54, ResponderBytes: 0, NAPPolicy: Balanced Security and Connectivity, DNSResponseType: No Error, Sinkhole: Unknown, URLCategory: Unknown, URLReputation: Risk unknown\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="cisco:firepower:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
