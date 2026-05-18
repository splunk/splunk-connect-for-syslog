# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape
import shortuuid

from .sendmessage import sendsingle
from .splunkutils import  splunk_single

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


test_cases = [
    'EEMI Audit event from device with { IP } 1.1.1.1 { HostName } {{ host }} { Severity } Warning { MessageID } MSG0001 { Message } Description: Login attempt alert for OME_c3b3edfr4 from 192.168.0.0.1 using REDFISH, IP will be blocked for 60 seconds. - System Display Name: iDRAC - System Service Tag: N97D5 - FQDN: {{ host }} - FQDD: iDRAC.Embedded.1 - Chassis Service Tag: N97D5  { Recommended Action } Contact the iDRAC administrator and make sure the username and password credentials used are correct. Check the Lifecycle Controller Log (LC Log) to see if more unauthorized iDRAC access attempts are occurring than would be expected due to forgotten account names or passwords.',
]


@pytest.mark.parametrize("case", test_cases)
@pytest.mark.addons("dell")
def test_dell_ome(
    record_property, setup_splunk, setup_sc4s, case
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    mt = env.from_string(case + "\n")
    message = mt.render(host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops sourcetype="dell:ome" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
