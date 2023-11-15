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

#Apr 01 14:30:23 darktraceserver1.mydomain.com darktrace_audit {"username":"jsmith","method":"POST","endpoint":"/login","ip":"10.72.62.2","status":302,"description":"Failed login"}
@pytest.mark.addons("darktrace")
def test_darktrace_audit(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, time, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} darktrace_audit {"username":"test","method":"POST","endpoint":"/login","ip":"10.72.62.2","status":302,"description":"Failed login"}'
    )
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host={{ host }} sourcetype="darktrace:audit"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#Apr 01 14:39:18 darktraceserver1.mydomain.com darktrace {"child_id":null,"last_updated":1648817054.504227,"message":"Unidirectional Traffic on subnet 10.12.12.0/24 is high (22.0%). This means that Darktrace may experience issues tracking devices on your network.\n\nIf you have any issues, please open a ticket using the following link. https://customerportal.darktrace.com/ticket/create","name":"high-unidirectional-traffic-10-12-12-0/24","uuid":"88cf2a43-61b9-4016-b9a6-12c900965f32","ip_address":"10.12.19.57","alert_name":"High Unidirectional Traffic","acknowledge_timeout":null,"priority":53,"status":"Active","hostname":"td-8294-05","priority_level":"medium","last_updated_status":1648817054.504227,"url":"https://darktraceserver1.serco-na.com/sysstatus?alert=87cf2a43-61b1-4006-b9a6-12c900915f72"}
@pytest.mark.addons("darktrace")
def test_darktrace_default(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, time, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} darktrace {"child_id":null,"last_updated":1648817054.504227,"message":"Unidirectional Traffic on subnet 10.12.12.0/24 is high (22.0%). This means that Darktrace may experience issues tracking devices on your network.\\n\\nIf you have any issues, please open a ticket using the following link. https://customerportal.darktrace.com/ticket/create","name":"high-unidirectional-traffic-10-12-12-0/24","uuid":"88cf2a43-61b9-4016-b9a6-12c900965f32","ip_address":"10.12.19.57","alert_name":"High Unidirectional Traffic","acknowledge_timeout":null,"priority":53,"status":"Active","hostname":"td-8294-05","priority_level":"medium","last_updated_status":1648817054.504227,"url":"https://darktraceserver1.serco-na.com/sysstatus?alert=87cf2a43-61b1-4006-b9a6-12c900915f72"}'
    )
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host={{ host }} sourcetype="darktrace"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
