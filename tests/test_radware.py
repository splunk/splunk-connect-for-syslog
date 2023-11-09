# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <110>M_00796:  User radware Session with client radware was terminated due to Inactivity.
@pytest.mark.addons("radware")
def test_radware_sample_1(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}M_00796:  User {{key}} Session with client radware was terminated due to Inactivity.\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search index=netops sourcetype=radware:defensepro "{{key}}"')
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <109>[Device: DP01 10.200.193.135] M_20000: 2 attacks of type "Intrusions" started between 15:36:06 UTC and 15:36:21 UTC. Detected by policiess: 206-212-144-0-POL, 206-212-128-0-POL; Attack name: DNS-named-version-attempt-UDP; Source IP: 92.1.1.1; Destination IPs: 206.1.1.1, 206.11.1.1; Destination port: 53; Action: drop.
@pytest.mark.addons("radware")
def test_radware_sample_2(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{mark}}[Device: {{key}} 10.200.193.135] M_20000: 2 attacks of type "Intrusions" started between 15:36:06 UTC and 15:36:21 UTC. Detected by policiess: 206-212-144-0-POL, 206-212-128-0-POL; Attack name: DNS-named-version-attempt-UDP; Source IP: 92.1.1.1; Destination IPs: 206.1.1.1, 206.11.1.1; Destination port: 53; Action: drop.\n'
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops host={{key}} sourcetype=radware:defensepro"
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
