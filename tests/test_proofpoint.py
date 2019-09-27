# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


# Apr 17 18:33:26 aplegw01 filter_instance1[195529]: rprt s=2hdryp02r6 m=1 x=2hdryp02r6-1 cmd=send profile=mail qid=w3HMWjG3039079 rcpts=rfaircloth@splunk.com
def test_proofpoint_pps_filter(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} filter_instance1[195529]: rprt s=2hdryp02r6 m=1 x=2hdryp02r6-1 cmd=send profile=mail qid=w3HMWjG3039079 rcpts=rfaircloth@splunk.com\n")
    message = mt.render(mark="<166>", host=host)

    sendsingle(message)

    st = env.from_string("search index=email host=\"{{ host }}\" sourcetype=\"pps_filter_log\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 17 18:35:26 aplegw02 sendmail[56106]: w3HMZPVT056101: to=<rfaircloth@splunk.com>, delay=00:00:01, xdelay=00:00:01, mailer=esmtp, tls_verify=FAIL, pri=133527, relay=mx1.splunk.iphmx.com. [216.71.153.223], dsn=2.0.0, stat=Sent (ok:  Message 22675962 accepted)
def test_proofpoint_pps_mail(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} pps-{{ host }} sendmail[195529]: w3HMZPVT056101: to=<rfaircloth@splunk.com>, delay=00:00:01, xdelay=00:00:01, mailer=esmtp, tls_verify=FAIL, pri=133527, relay=mx1.splunk.iphmx.com. [216.71.153.223], dsn=2.0.0, stat=Sent (ok:  Message 22675962 accepted)\n")
    message = mt.render(mark="<166>", host=host)

    sendsingle(message)

    st = env.from_string("search index=email host=\"pps-{{ host }}\" sourcetype=\"pps_mail_log\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

