import uuid
import random

from jinja2 import Environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment()


# <38>1 2020-07-21T21:05:56+02:00 localhost prg00000 1234 - - ﻿seq: 0000000000, thread: 0000, runid: 1595365556, stamp: 2020-07-21T21:05:56 PADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPAD
def test_loggen_rfc(record_property,  setup_splunk, setup_sc4s):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    epoch = epoch[:-3]
    mt = env.from_string(
        "<38>1 {{ iso }} {{ host }} prg00000 1234 - - ﻿seq: 0000000000, thread: 0000, runid: 1595365556, stamp: {{iso}} PADDPADDPADDPADDPADDP\n"
    )
    message = mt.render(iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}"  sourcetype="syslogng:loggen"'
    )
    search = st.render(epoch=epoch, host=host)
    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <38>2020-07-24T17:04:52 localhost prg00000[1234]: seq: 0000000008, thread: 0000, runid: 1595610292, stamp: 2020-07-24T17:04:52 PADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADD
def test_loggen_bsd(record_property,  setup_splunk, setup_sc4s):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"

    dt = datetime.datetime.now()

    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]
    mt = env.from_string(
        "<38>{{iso}} {{ host }} prg00000[1234]: seq: 0000000008, thread: 0000, runid: 1595610292, stamp: {{iso}} PADDPADDPADDPADDPADDPADDPADDPADDPADDPADDPADDBSD\n"
    )
    message = mt.render(iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}"  sourcetype="syslogng:loggen"'
    )
    search = st.render(epoch=epoch, host=host)
    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
