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
#<27>Jan 25 01:58:06 filterlog: 82,,,1000002666,mvneta2,match,pass,out,6,0x00,0x00000,64,ICMPv6,58,8,fe80::208:a2ff:fe0f:cb66,fe80::56a6:5cff:fe7d:1d43,
def test_pfsense_filterlog(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{mark}}{% now 'local', '%b %d %H:%M:%S' %} filterlog: 82,,,1000002666,mvneta2,match,pass,out,6,0x00,0x00000,64,ICMPv6,58,8,{{key}},\n")
    message = mt.render(mark="<27>", key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5006])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netfw sourcetype=pfsense:filterlog \"{{key}}\" earliest=-2m | head 2")
    search = st.render(key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<27>Jan 25 01:58:06 kqueue error: unknown
def test_pfsense_other(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{mark}}{% now 'local', '%b %d %H:%M:%S' %} kqueue error: {{key}}\n")
    message = mt.render(mark="<27>", key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5006])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netops sourcetype=pfsense:* \"{{key}}\" earliest=-2m | head 2")
    search = st.render(key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<27>Jan 25 01:58:06 syslogd: restart
def test_pfsense_syslogd(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{mark}}{% now 'local', '%b %d %H:%M:%S' %} syslogd: restart {{key}}\n")
    message = mt.render(mark="<27>", key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5006])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netops sourcetype=pfsense:syslogd \"{{key}}\" earliest=-2m | head 2")
    search = st.render(key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
