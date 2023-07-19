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

#
# <189> Oct 21 09:10:54 10.201.1.110-1 CMDLOGGER[emWeb]: cmd_logger_api.c(83) 29333 %% NOTE CLI:10.1.3.211:administrator:User  logged in
# <189> Oct 21 09:10:20 10.201.1.110-1 TRAPMGR[trapTask]: traputil.c(721) 29331 %% NOTE 'startup-config' has changed.
# <190> Oct 21 09:10:20 10.201.1.110-1 UNITMGR[emWeb]: unitmgr.c(6905) 29330 %% INFO Configuration propagation successful for config type 0


testdata_admin = [
    "{{ mark }} {{ bsd }} {{ host }}-1 CMDLOGGER[emWeb]: cmd_logger_api.c(83) 29333 %% NOTE CLI:10.1.3.211:administrator:User  logged in",
    "{{ mark }} {{ bsd }} {{ host }}-1 TRAPMGR[trapTask]: traputil.c(721) 29331 %% NOTE 'startup-config' has changed.",
    "{{ mark }} {{ bsd }} {{ host }}-1 UNITMGR[emWeb]: unitmgr.c(6905) 29330 %% INFO Configuration propagation successful for config type 0",
]


@pytest.mark.parametrize("event", testdata_admin)
def test_dell_emc_powerswitch_nseries(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="dell:emc:powerswitch:n" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
