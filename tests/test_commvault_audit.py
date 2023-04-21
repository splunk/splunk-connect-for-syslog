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

def test_commvault_audit_event(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        "AuditTrail: Opid = {119276} Audittime = {21 Oct 2022 11:58:05} Severitylevel = {High} Operation = {User account locked} Details = { Login attempts for user [DOMAINNAME\{{ host }}] exceeded limit. Account is locked for [5minute(s)]}"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netfw sourcetype="commvault:syslog" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
