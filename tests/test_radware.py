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

# <110>M_00796:  User radware Session with client radware was terminated due to Inactivity.
def test_radware_sample_1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}M_00796:  User {{key}} Session with client radware was terminated due to Inactivity.\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search index=netops sourcetype=radware:defensepro "{{key}}"')
    search = st.render(epoch=epoch, key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <109>[Device: DP01 10.200.193.135] M_20000: 2 attacks of type "Intrusions" started between 15:36:06 UTC and 15:36:21 UTC. Detected by policiess: 206-212-144-0-POL, 206-212-128-0-POL; Attack name: DNS-named-version-attempt-UDP; Source IP: 92.1.1.1; Destination IPs: 206.1.1.1, 206.11.1.1; Destination port: 53; Action: drop.
def test_radware_sample_2(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}[Device: {{key}} 10.200.193.135] M_20000: 2 attacks of type \"Intrusions\" started between 15:36:06 UTC and 15:36:21 UTC. Detected by policiess: 206-212-144-0-POL, 206-212-128-0-POL; Attack name: DNS-named-version-attempt-UDP; Source IP: 92.1.1.1; Destination IPs: 206.1.1.1, 206.11.1.1; Destination port: 53; Action: drop.\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search index=netops host={{key}} sourcetype=radware:defensepro')
    search = st.render(epoch=epoch, key=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
