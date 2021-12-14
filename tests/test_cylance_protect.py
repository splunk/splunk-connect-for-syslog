# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import random
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <46>1 2021-12-08T21:07:19.100000Z sysloghost CylancePROTECT - - - Event Type: ExploitAttempt, Event Name: none, Device Name: DEVICENAME, IP Address: (), Action: None, Process ID: 72724, Process Name: C:\Program Files (x86)\Medcon\Medcon Common\Dicom2Avi_App.exe, User Name: tcsadmin, Violation Type: Stack Pivot, Zone Names: (Windows Server 2008), Device Id: a603a6e8-cac7-4d06-970c-24671e5af6cc, Policy Name: Servers Complete Policy


def test_cylance_exploit(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
