# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest
import random
import pytz

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("a10networks")
def test_a10_vthunder(
    record_property, setup_splunk, setup_sc4s
):
    mt = env.from_string(
       "{{ mark }} CEF:0|A10|vThunder|4.1.4-GR1-P12|WAF|session-id|2|rt={{ bsd }} src=1.1.1.1 spt=34860 dst=1.1.1.1 dpt=80 dhost=test.host.local cs1=uiext_sec_waf cs2=1 act=learn cs3=learn app=HTTP requestMethod=GET cn1=0 request=/sales/ msg=New session created: Id\=1\n"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=dt.strftime("%b %d %Y %H:%M:%S"))

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netwaf sourcetype="a10networks:vThunder:cef" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("a10networks")
def test_a10_vthunder_syslog(
    record_property, setup_splunk, setup_sc4s, get_host_key
):
    host = get_host_key
    mt = env.from_string(
        "{{mark}} {{bsd}} {{host}} a10logd: [audit log]{{mark}} Partition: shared,  [admin] web: [222:1.1.1.1:22222] RESP HTTP status 200 OK"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=bsd, host=host)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netops sourcetype="a10networks:vThunder:syslog" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1