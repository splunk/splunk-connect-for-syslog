# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# https://www.ciscolive.com/c/dam/r/ciscolive/us/docs/2017/pdf/TECUCC-3000.pdf

# <190>: 2020 Oct 26 10:33:18 CET: %UCSM-6-AUDIT: [session][internal][creation][internal][3852391][sys/user-ext/web-login-username-web_40207_B][id:web_40207_B, name:username, policyOwner:local][] Web B: remote user username logged in from ipaddr


@pytest.mark.addons("cisco")
def test_cisco_ucm_manager(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}: {{ bsd }} {{ tzname }} : %UCSM-6-AUDIT: [session][internal][creation][internal][3852391][sys/user-ext/web-login-username-web_40207_B][id:web_40207_B, name:username, policyOwner:local][] Web B: remote user username logged in from {{ host }}\n"
    )
    message = mt.render(mark="<189>", tzname=tzname, bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops {{ host }} sourcetype="cisco:ucs"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
