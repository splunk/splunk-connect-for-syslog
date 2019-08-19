# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from flaky import flaky
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


@flaky(max_runs=3, min_passes=2)
def test_bluecoatproxySG_kv(record_property, setup_wordlist, setup_splunk):
    csHost = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r"{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %}.000z  \"sample_logs bluecoat[0]:SPLV5.1 c-ip=192.0.0.10 Content-Type=\"application/json;%20charset=UTF-8\" cs-bytes=5006 cs-categories=\"unavailable;Technology/Internet\" cs-host={{ csHost }} cs-ip=192.0.0.10 cs-method=POST cs-uri-path=/en-US/splunkd/__raw/services/messages cs-uri-query=\"?output_mode=json&sort_key=timeCreated_epochSecs&sort_dir=desc&count=1000&_=1424933765619\" cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent=\"Mac OS X/10.10.2 (14C109)\" cs-username=user2 clientduration=0 rs-status=0 rs_Content_Type=application/json;%20charset=UTF-8 s-action=TCP_NC_MISS s-ip=10.0.0.10 serveripservice.name=\"Explicit HTTP\" service.group=\"Standard\" s-supplier-ip=10.0.0.10 s-supplier-name=gh.ij.kl.com sc-bytes=9646 sc-filter-result=DENIED sc-status=400 time-taken=20 x-bluecoat-appliance-name=\"10.0.0.10-sample_logs\" x-bluecoat-appliance-primary-address=10.0.0.10 x-bluecoat-proxy-primary-address=10.0.0.10 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed x-exception-id=invalid_request c-url=\"http://randomserver:8000/en-US/app/examples/\" cs-Referer=\"http://randomserver:8000/en-US/app/examples/\"")
    message = mt.render(mark="<134>", csHost=csHost)
    sendsingle(message)

    st = env.from_string("search index=main cs_host=\"{{ csHost }}\" sourcetype=\"bluecoat:proxysg:access:kv\" | head 2")
    search = st.render(csHost=csHost)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("cs_host", csHost)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
def test_bluecoatproxySG_syslog(record_property, setup_wordlist, setup_splunk):
    csHost = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r"{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} sample_logs: info: 2019-08-15 19:42:52 63055 192.0.0.10  user2 - - OBSERVED \"unavailable;Technology/Internet\" http://samppleserver:8000/en-US/account/login?return_to=%2Fen-US%2Fsample_app%2Fexamples 304 TCP_HIT GET application/json;%20charset=UTF-8 http {{ csHost }} 80 /en-US/splunkd/__raw/servicesNS/admin/simple_xml_examples/data/ui/views ?output_mode=json&count=-1&digest=1&_=1424960631237 - \"ocspd/1.0.3\" 10.0.0.10 2252 2099 - - -")
    message = mt.render(mark="<134>", csHost=csHost)
    sendsingle(message)

    st = env.from_string("search index=main cs_host=\"{{ csHost }}\" sourcetype=\"bluecoat:proxysg:access:syslog\" | head 2")
    search = st.render(csHost=csHost)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("cs_host", csHost)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
def test_bluecoatproxySG_otherSyslog(record_property, setup_wordlist, setup_splunk):
    csHost = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r'2019-08-16 17:38:20 24123 192.0.0.5 user5 - jjj.kk.com 192.0.0.5 Country2 - - OBSERVED "Web Ads/Analytics" http://random/url/abc 200 TCP_NC_MISS CONNECT application/json;%20charset=UTF-8 tcp {{csHost}} 80 /en-US/splunkd/__raw/servicesNS/admin/simple_xml_examples/search/jobs ?output_mode=json - "ocspd/1.0.3" 10.0.0.5 11831777 15764 - "none" "none" unavailable' )
    message = mt.render(mark="<134>", csHost=csHost)
    sendsingle(message)

    st = env.from_string("search index=main cs_host=\"{{ csHost }}\" sourcetype=\"bluecoat:proxysg:access:syslog\" | head 2")
    search = st.render(csHost=csHost)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("cs_host", csHost)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
def test_bluecoatproxySG_access(record_property, setup_wordlist, setup_splunk):
    csHost = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r'date="2019-08-15" time="23:08:04" time-taken="7948" c-ip="192.0.0.9" cs-username="user1" cs-auth-group="-" x-exception-id="-" sc-filter-result="PROXIED" cs-categories="unavailable;Technology/Internet" cs_Referer="-" sc-status="0" s-action="FAILED" cs-method="GET" rs_Content_Type="text/plain" cs-uri-scheme="http" cs-host="{{csHost}}" cs-uri-port="8000" cs-uri-path="/l1k-chain256.cer" cs-uri-query="-" cs-uri-extension="cer" cs_User_Agent="ocspd/1.0.3" s-ip="10.0.0.9" sc-bytes="5132" cs-bytes="26" x-virus-id="-" x-bluecoat-application-name="-" x-bluecoat-application-operation="-" category="unavailable"')
    message = mt.render(mark="<134>", csHost=csHost)
    sendsingle(message)

    st = env.from_string("search index=main cs_host=\"{{ csHost }}\" sourcetype=\"bluecoat:proxysg:access:file\" | head 2")
    search = st.render(csHost=csHost)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("cs_host", csHost)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
def test_bluecoatproxySG_unknown(record_property, setup_wordlist, setup_splunk):
    csHost = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r'{{ mark }}  sample_logs: info: 2019-08-15 19:42:52 63055 192.0.0.10 date="2019-08-15" time="23:08:04" time-taken="7948" c-ip="192.0.0.9" cs-username="user1" cs-auth-group="-" x-exception-id="-" sc-filter-result="PROXIED" cs-categories="unavailable;Technology/Internet" cs_Referer="-" sc-status="0" s-action="FAILED" cs-method="GET" rs_Content_Type="text/plain" cs-uri-scheme="http" cs-host="{{csHost}}" cs-uri-port="8000" cs-uri-path="/l1k-chain256.cer" cs-uri-query="-" cs-uri-extension="cer" cs_User_Agent="ocspd/1.0.3" s-ip="10.0.0.9" sc-bytes="5132" cs-bytes="26" x-virus-id="-" x-bluecoat-application-name="-" x-bluecoat-application-operation="-" category="unavailable"')
    message = mt.render(mark="<134>", csHost=csHost)
    sendsingle(message)

    st = env.from_string("search index=main cs_host=\"{{ csHost }}\" sourcetype=\"bluecoat:proxysg:access:unknown\" | head 2")
    search = st.render(csHost=csHost)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("cs_host", csHost)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1