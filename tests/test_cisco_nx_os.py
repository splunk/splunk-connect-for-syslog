# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

# Nov 1 14:07:58 excal-113 %MODULE-5-MOD_OK: Module 1 is online
def test_cisco_nx_os(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} csconx-{{ host }} %MODULE-5-MOD_OK: Module 1 is online")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netops host=\"csconx-{{ host }}\" sourcetype=\"cisco:ios\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Nov 1 14:07:58 excal-113 %MODULE-5-MOD_OK: Module 1 is online
# @pytest.mark.xfail
#def test_cisco_nx_os_singleport(record_property, setup_wordlist, get_host_key, setup_splunk):
#    host = get_host_key
#
#    mt = env.from_string(
#        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} %MODULE-5-MOD_OK: Module 1 is online")
#    message = mt.render(mark="<23>", host=host)
#
#    sendsingle(message, host="sc4s-nx-os")
#
#    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:ios\" | head 2")
#    search = st.render(host=host)
#
#    resultCount, eventCount = splunk_single(setup_splunk, search)
#
#    record_property("host", host)
#    record_property("resultCount", resultCount)
#    record_property("message", message)
#
#    assert resultCount == 1