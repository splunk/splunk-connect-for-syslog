# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

#<11>July 22 22:45:28 apic1 %LOG_LOCAL0-2-SYSTEM_MSG [F0110][soaking][node-failed][critical][topology/pod-1/node-102/fault-F0110] Node 102 not reachable. unknown
def test_cisco_aci(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} %LOG_LOCAL0-2-SYSTEM_MSG [F0110][soaking][node-failed][critical][topology/pod-1/node-102/fault-F0110]\n")
    message = mt.render(mark="<165>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netops host=\"{{ host }}\" sourcetype=\"cisco:apic:events\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#%ACLLOG-5-ACLLOG_PKTLOG
def test_cisco_aci_acl(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} %ACLLOG-5-ACLLOG_PKTLOG unable to locate real message\n")
    message = mt.render(mark="<165>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"cisco:apic:acl\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
