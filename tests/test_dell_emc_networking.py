# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <189> Oct 21 09:10:54 test-dell-switch-n-1 CMDLOGGER[emWeb]: cmd_logger_api.c(83) 29333 %% NOTE CLI:10.1.3.211:administrator:User  logged in
# <189> Oct 21 09:10:20 test-dell-switch-n-2 TRAPMGR[trapTask]: traputil.c(721) 29331 %% NOTE 'startup-config' has changed.
# <190> Oct 21 09:10:20 test-dell-switch-n-3 UNITMGR[emWeb]: unitmgr.c(6905) 29330 %% INFO Configuration propagation successful for config type 0

test_cases = [
    "{{ mark }} {{ bsd }} {{ host }} CMDLOGGER[emWeb]: cmd_logger_api.c(83) 29333 %% NOTE CLI:10.1.3.211:administrator:User  logged in",
    "{{ mark }} {{ bsd }} {{ host }} TRAPMGR[trapTask]: traputil.c(721) 29331 %% NOTE 'startup-config' has changed.",
    "{{ mark }} {{ bsd }} {{ host }} UNITMGR[emWeb]: unitmgr.c(6905) 29330 %% INFO Configuration propagation successful for config type 0",
]


@pytest.mark.parametrize("case", test_cases)
def test_dell_emc_powerswitch_nseries(
    record_property, setup_splunk, setup_sc4s, case
):
    host = f'test-dell-switch-n-{test_cases.index(case)}'

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(case + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="dell:emc:powerswitch:n" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
