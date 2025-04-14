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

# <30>Jul 15 18:03:54 NAShostname qulogd[13241]: conn log: Users: admin, Source IP: 10.0.0.1, Computer name: ---, Connection type: HTTP, Accessed resources: ---, Action: Logout
# <30>Jul 15 18:06:46 NAShostname qulogd[13241]: conn log: Users: admin, Source IP: 10.0.0.1, Computer name: localhost, Connection type: SMB, Accessed resources: Multimedia/folder/file.txt, Action: Read
def test_qnap_nas_qts(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} qnap-{{host}} qulogd[13241]: conn log: Users: admin, Source IP: 10.0.0.1, Computer name: localhost, Connection type: SMB, Accessed resources: Multimedia/folder/file.txt, Action: Read"
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=infraops sourcetype=qnap:syslog host=qnap-{{host}}"
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
