# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from flaky import flaky
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


#@flaky(max_runs=3, min_passes=2)
def test_defaultroute(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"syslog:fallback\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#@flaky(max_runs=3, min_passes=2)
def test_tag(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} testvp-{{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"testvp-{{ host }}\" sourcetype=\"syslog:fallback\" | spath \"_metadata.vendor_product\" | search \"_metadata.vendor_product\"=\"test_test\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1