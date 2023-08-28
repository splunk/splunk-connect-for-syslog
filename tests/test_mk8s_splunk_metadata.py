# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid
import sys

from jinja2 import Environment, select_autoescape
from pytest import mark

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

@pytest.mark.skipif(sys.platform != 'darwin', reason='it should not run in CICD')
def test_splunk_metadata(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"testcm-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch_ms = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ epoch }}123 {{ host }} security_event ids_alerted signature=1:28423:1 priority=1 timestamp={{ epoch }} dhost=98:5A:EB:E1:81:2F direction=ingress protocol=tcp/ip src=151.101.52.238:80 dst=192.168.128.2:53023 message: EXPLOIT-KIT Multiple exploit kit single digit exe detection\n"
    )
    message = mt.render(mark="<134>", epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9001])

    st = env.from_string(
        'search _time={{ epoch_ms }} index=netops host="{{ host }}" '
    )
    search = st.render(epoch_ms=epoch_ms, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
