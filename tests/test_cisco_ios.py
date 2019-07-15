# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


# <190>30: foo: *Apr 29 13:58:46.411: %SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 192.168.1.239 stopped - CLI initiated
def test_cisco_ios(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }}{{ seq }}: {{ host }}: *{% now 'utc', '%b %d %H:%M:%S' %}.100: CET: %SEC-6-IPACCESSLOGP: list 110 denied tcp 54.122.123.124(8932) -> 10.1.0.1(22), 1 packet\n")
    message = mt.render(mark="<166>", seq=20, host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:ios\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
