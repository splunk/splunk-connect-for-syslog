# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# Nov 1 14:07:58 excal-113 %MODULE-5-MOD_OK: Module 1 is online
def test_cisco_nx_os(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} csconx-{{ host }} %MODULE-5-MOD_OK: Module 1 is online")
    message = mt.render(mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netops host=\"csconx-{{ host }}\" sourcetype=\"cisco:ios\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Nov 1 14:07:58 excal-113 %MODULE-5-MOD_OK: Module 1 is online
# @pytest.mark.xfail
#def test_cisco_nx_os_singleport(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s):
#    host = get_host_key
#
#    dt = datetime.datetime.now()
#    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
#
#    # Tune time functions
#    epoch = epoch[:-7]
#
#    mt = env.from_string(
#        "{{ mark }} {{ bsd }} {{ host }} %MODULE-5-MOD_OK: Module 1 is online")
#    message = mt.render(mark="<23>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
#
#    sendsingle(message, host="sc4s-nx-os")
#
#    st = env.from_string("search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ios\"")
#    search = st.render(epoch=epoch, host=host)
#
#    resultCount, eventCount = splunk_single(setup_splunk, search)
#
#    record_property("host", host)
#    record_property("resultCount", resultCount)
#    record_property("message", message)
#
#    assert resultCount == 1
