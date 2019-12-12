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
import random

env = Environment(extensions=['jinja2_time.TimeExtension'])

def test_symantec_ep_msg_1(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} SymantecServer: WORK1-PC,Local Host: 0.0.0.0,Local Port: 29555,Local Host MAC: FFFFFFFFFFFF,Remote Host IP: 0.0.0.0,Remote Host Name: ,Remote Port: 0,Remote Host MAC: WORK2-PC,7,Inbound,Begin: 2019-10-25 00:06:22,End: 2019-10-25 00:06:22,Occurrences: 1,Application: ,Rule: B-ALL-B,Location: Untrusted,User: johndoe,Domain: AD-ENT,Action: Blocked,SHA-256: ,MD-5:\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_symantec_ep_msg_two(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} SymantecServer: WORK1-PC,Local Host: 192.168.1.85,Local Port: 59929,Local Host MAC: D4D252E652BA,Remote Host IP: 10.217.138.110,Remote Host Name: host.example.com,Remote Port: 9000,Remote Host MAC: D4B17A775938,TCP,Outbound,Begin: 2019-10-25 00:06:09,End: 2019-10-25 00:06:18,Occurrences: 3,Application: C:/Program Files/Preton/PretonSaver/PretonService.exe,Rule: B-ALL-B,Location: Untrusted,User: SYSTEM,Domain: NT AUTHORITY,Action: Blocked,SHA-256: ba532f64bd6a31cf5f1938820f458d31fed8faa01733c9de3a1d313198b0dd9c,MD-5: 1AE7578A3CF3EABE492463C2AB7D7318\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_symantec_ep_msg_two(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} SymantecServer: Site: WORK-A,Server: FOOFOO,Domain: Desktop,The client has downloaded the content package successfully,FOOFO,USERNAME,ENT.EXAMPLE.CORP\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1