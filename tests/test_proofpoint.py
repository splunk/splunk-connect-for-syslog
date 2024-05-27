# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Apr 17 18:33:26 aplegw01 filter_instance1[195529]: rprt s=2hdryp02r6 m=1 x=2hdryp02r6-1 cmd=send profile=mail qid=w3HMWjG3039079 rcpts=rfaircloth@splunk.com
@pytest.mark.addons("proofpoint")
def test_proofpoint_pps_filter(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = "pps-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} filter_instance1[195529]: rprt s=2hdryp02r6 m=1 x=2hdryp02r6-1 cmd=send profile=mail qid=w3HMWjG3039079 rcpts=rfaircloth@splunk.com\n"
    )
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email host="{{ host }}" sourcetype="pps_filter_log"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 17 18:35:26 aplegw02 sendmail[56106]: w3HMZPVT056101: to=<rfaircloth@splunk.com>, delay=00:00:01, xdelay=00:00:01, mailer=esmtp, tls_verify=FAIL, pri=133527, relay=mx1.splunk.iphmx.com. [216.71.153.223], dsn=2.0.0, stat=Sent (ok:  Message 22675962 accepted)
@pytest.mark.addons("proofpoint")
def test_proofpoint_pps_mail(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = "pps-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} pps-{{ host }} sendmail[195529]: w3HMZPVT056101: to=<rfaircloth@splunk.com>, delay=00:00:01, xdelay=00:00:01, mailer=esmtp, tls_verify=FAIL, pri=133527, relay=mx1.splunk.iphmx.com. [216.71.153.223], dsn=2.0.0, stat=Sent (ok:  Message 22675962 accepted)\n"
    )
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email host="pps-{{ host }}" sourcetype="pps_mail_log"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
