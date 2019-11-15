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

def test_defaultroute(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"sc4s:fallback\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_internal(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main NOT host=\"{{ host }}\" sourcetype=\"sc4s:events\" | head 1")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_tag(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} testvp-{{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"testvp-{{ host }}\" sourcetype=\"sc4s:fallback\" sc4s_vendor_product=test_test | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
def test_metrics(record_property, setup_wordlist, setup_splunk):

    st = env.from_string('mcatalog values(metric_name) WHERE metric_name="syslogng.d_*#0" AND ("index"="*" OR "index"="_*") BY index | fields index')
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 1

def test_tz_guess(record_property, setup_wordlist, setup_splunk):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'America/Los_Angeles', '%b %d %H:%M:%S' %} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"cisco:asa\" \"%ASA-3-003164\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

