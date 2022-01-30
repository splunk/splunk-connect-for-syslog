# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest

env = Environment()


# <134>Jan 27 14:29:26 nasapi[19090] - log - set_config - INFO- success
testdata = [
    "{{ mark }}{{ bsd }} nasapi[19090] - log - {{ host }} - INFO- success",
]
# Test disabled for now source doesn't provide host name

# @pytest.mark.parametrize("event", testdata)
# def test_buffalo_terastation(
#     record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
# ):
#     host = get_host_key

#     dt = datetime.datetime.now()
#     iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

#     # Tune time functions
#     epoch = epoch[:-7]

#     mt = env.from_string(event + "\n")
#     message = mt.render(mark="<166>", bsd=bsd, host=host)

#     sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

#     st = env.from_string(
#         'search index=infraops _time={{ epoch }} sourcetype="buffalo:terrastation:nasapi" "{{ host }}")'
#     )
#     search = st.render(epoch=epoch, host=host)

#     resultCount, eventCount = splunk_single(setup_splunk, search)

#     record_property("host", host)
#     record_property("resultCount", resultCount)
#     record_property("message", message)

#     assert resultCount == 1
