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

# <111>1 2022-01-05T15:59:32.482Z our_sc4s_VIP.fqdn DNAC - - - {"version":"1.0.0","instanceId":"temp-instance","eventId":"NETWORK-DEVICES-1-1","namespace":"ASSURANCE","name":"AP License Exhausted on WLC","description":"WLC currently has no free AP licenses","type":"NETWORK","category":"WARN","domain":"Know Your Network","subDomain":"Devices","severity":3,"source":"EXTERNAL","timestamp":1641398372477,"details":{"Type":"","Assurance Issue Priority":"","Assurance Issue Details":"This WLC  is currently licensed to support  AP(s) and is now operating at its full licensed capacity. No additional AP can join this WLC.","Device":"","Assurance Issue Category":"","Assurance Issue Name":"WLC  currently has no free AP licenses.","Assurance Issue Status":""},"ciscoDnaEventLink":"https://&lt;DNAC_IP_ADDRESS&gt;/dna/assurance/issueDetails?issueId=","note":"To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=1234-12bb-1e23-a1e2","tntId":"1ccccfe2b34567890c123456","context":"EXTERNAL","userId":null,"i18n":null,"eventHierarchy":null,"message":null,"messageParams":null,"parentInstanceId":null,"network":null,"isSimulated":true,"startTime":65247136409219,"dnacIP":null,"tenantId":"tempid"}

@pytest.mark.addons("cisco")
def test_cisco_dna(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} DNAC - - - {"version":"1.0.0","instanceId":"{{ host }} ","eventId":"NETWORK-DEVICES-1-1","namespace":"ASSURANCE","name":"AP License Exhausted on WLC","description":"WLC currently has no free AP licenses","type":"NETWORK","category":"WARN","domain":"Know Your Network","subDomain":"Devices","severity":3,"source":"EXTERNAL","timestamp":{{ epoch }},"details":{"Type":"","Assurance Issue Priority":"","Assurance Issue Details":"This WLC  is currently licensed to support  AP(s) and is now operating at its full licensed capacity. No additional AP can join this WLC.","Device":"","Assurance Issue Category":"","Assurance Issue Name":"WLC  currently has no free AP licenses.","Assurance Issue Status":""},"ciscoDnaEventLink":"https://&lt;DNAC_IP_ADDRESS&gt;/dna/assurance/issueDetails?issueId=","note":"To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=1234-12bb-1e23-a1e2","tntId":"1ccccfe2b34567890c123456","context":"EXTERNAL","userId":null,"i18n":null,"eventHierarchy":null,"message":null,"messageParams":null,"parentInstanceId":null,"network":null,"isSimulated":true,"startTime":65247136409219,"dnacIP":null,"tenantId":"tempid"}'
    )
    message = mt.render(mark="<111>1", bsd=bsd, host=host, date=date, time=time, iso=iso, epoch = epoch)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops {{ host }} sourcetype="cisco:dna"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
