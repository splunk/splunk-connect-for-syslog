# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))
#<86>1 2023-06-01T15:57:33.760Z 10.164.2.132 SecureAuth2 2928 ID90020 [SecureAuth@27389 UserAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36" UserHostAddress="10.1.2.2" RequestID="d2014021-4e06-45c6-a580-346e12346b60" Realm="SecureAuth2" Appliance="SecureAuth05VM.domain.com" Company="National Title Group Inc" Version="9.2.0.85" PEN="27389" HostName="10.1.2.2" Category="AUDIT" Priority="4" EventID="90020"] Application - Begin request

@pytest.mark.addons("secureauth")
def test_secureauth(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} SecureAuth2 2000 ID00000 [SecureAuth@27389 UserAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/123.00 (KHTML, like Gecko) Chrome/10.0.0.0 Safari/123.00" UserHostAddress="10.0.0.0" RequestID="dddd000d-444e-45cc-aaas-346e12346b60" Realm="SecureAuth2" Appliance="SecureAuth05VM.domain.com" Company="National Title Group Inc" Version="1.0.0.01" PEN="12345" HostName="10.0.0.0" Category="AUDIT" Priority="4" EventID="10020"] Application - Begin request'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops  host={{ host }} sourcetype="secureauth:idp"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
