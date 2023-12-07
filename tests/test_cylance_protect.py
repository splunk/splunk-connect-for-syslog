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

# <46>1 2021-12-08T21:07:19.100000Z sysloghost CylancePROTECT - - - Event Type: ExploitAttempt, Event Name: none, Device Name: DEVICENAME, IP Address: (), Action: None, Process ID: 72724, Process Name: C:\Program Files (x86)\Medcon\Medcon Common\Dicom2Avi_App.exe, User Name: tcsadmin, Violation Type: Stack Pivot, Zone Names: (Windows Server 2008), Device Id: a603a6e8-cac7-4d06-970c-24671e5af6cc, Policy Name: Servers Complete Policy

@pytest.mark.addons("cylance")
def test_cylance_exploit(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }} {{ host }} CylancePROTECT - - - Event Type: ExploitAttempt, Event Name: none, Device Name: DEVICENAME"
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epintel host="{{ host }}" sourcetype="syslog_exploit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
