# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("tintri")
def test_tintri(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ iso }} {{ host }} : Scrubbed@ 2021-03-22T13:55:01.620956-04:00 tomcat: [https-jsse-nio-443-exec-8,com.tintri.log.LogBase] WARN : USER:AUDIT:LOG-AUDIT-0083: [358966] Reset credentials [POST /api/v310/userAccount/reset#012[Severity:WARNING , Facility:LOCAL6]\n"
    )
    message = mt.render(mark="<165>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="tintri"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
