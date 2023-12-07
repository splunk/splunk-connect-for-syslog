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


# Apr 15 2017 00:22:42 192.168.12.1 : %FWSM-6-106100: access-list outside-access-in ##permission## ##transport## outside/XXX.XXX.XXX.XXX(##port_1##) -> inside/XXX.XXX.XXX.XXX(9997) hit-cnt 1 (first hit) [0xe0ba389d, 0x0]
@pytest.mark.addons("cisco")
def test_cisco_pix_traditional(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} : %PIX-3-302022: Built inbound ICMP connection for faddr XXX.XXX.XXX.XXX/1 gaddr XXX.XXX.XXX.XXX/1 laddr XXX.XXX.XXX.XXX/0\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:pix"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
