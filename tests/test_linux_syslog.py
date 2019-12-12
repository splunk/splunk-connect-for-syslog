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

#<78>Oct 25 09:10:00 /usr/sbin/cron[54928]: (root) CMD (/usr/libexec/atrun)
def test_linux__nohost_program_as_path(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} /usr/sbin/cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux__host_program_as_path(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} /usr/sbin/cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" host={{ host }} sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux__nohost_program_conforms(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux__host_program_conforms(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} cron[{{ pid }}]: (root) CMD (/usr/libexec/atrun)\n")
    message = mt.render(mark="<111>", host=host, pid=pid)

    sendsingle(message)

    st = env.from_string("search index=main \"[{{ pid }}]\" host={{ host }} sourcetype=\"nix:syslog\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1