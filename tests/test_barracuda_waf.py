# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

def test_netapp_test_audit_event(
        record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }}{{ bsd }} -0600  waf-den TR {{ host }} 123 10.0.0.0 5000 "-" "-" GET TLSv1.2 fws.gov HTTP/1.1 200 1000 725 SERVER DEFAULT UNPROTECTED VALID /themes/custom/fws_gov/favicon.ico 10.0.0.0 50000 50'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<134>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="barracuda:waf" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
