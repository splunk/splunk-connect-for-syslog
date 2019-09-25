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


# Apr 15 2017 00:21:14 192.168.12.1 : %ASA-5-111010: User 'john', running 'CLI' from IP 0.0.0.0, executed 'dir disk0:/dap.xml'
# Apr 15 2017 00:22:27 192.168.12.1 : %ASA-4-313005: No matching connection for ICMP error message: icmp src outside:81.24.28.226 dst inside:72.142.17.10 (type 3, code 0) on outside interface. Original IP payload: udp src 72.142.17.10/40998 dst 194.153.237.66/53.
# Apr 15 2017 00:22:42 192.168.12.1 : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
def test_cisco_asa_traditional(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"cisco:asa\" \"%ASA-3-003164\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <166>2018-06-27T12:17:46Z asa : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
def test_cisco_asa_rfc5424(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%SZ' %} {{ host }} : %ASA-3-005424: TCP access denied by ACL from 179.236.133.160/5424 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<166>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"cisco:asa\" \"%ASA-3-005424\"| head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
