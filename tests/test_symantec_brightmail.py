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
# <141>Oct 24 21:05:43 smg-1 conduit: [Brightmail] (NOTICE:7500.3119331456): [12066] 'BrightSig3 Newsletter Rules' were updated successfully.
def test_symantec_brightmail(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'utc', '%b %d %H:%M:%S' %} {{host}} conduit: [Brightmail] (NOTICE:7500.3119331456): [12066] 'BrightSig3 Newsletter Rules' were updated successfully.")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=email host=\"{{ host }}\" sourcetype=\"symantec:smg\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
