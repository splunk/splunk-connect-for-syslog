# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import uuid
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <14>1 2021-12-08T21:14:32.063248Z xxxxxx-1 qumulo - - - 127.0.0.1,"admin",api,fs_read_metadata,ok,2,"/",""
def test_qumulo_storage(record_property,  setup_splunk, setup_sc4s):
    host = f"{uuid.uuid4().hex}-{uuid.uuid4().hex}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} qumulo - - - 127.0.0.1,"admin",api,fs_read_metadata,ok,2,"/",""'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="qumulo:storage"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
