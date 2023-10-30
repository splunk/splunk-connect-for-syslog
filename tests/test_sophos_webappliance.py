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

# <27>Mar 24 21:45:28 10.1.1.1 h=10.99.115.13 u="DOMAIN\\johnsmith" s=200 X=- t=1336666489 T=284453 Ts=0 act=1 cat="0x220000002a" app="-" rsn=- threat="-" type="text/html" ctype="text/html" sav-ev=4.77 sav-dv=2012.5.10.4770003 uri-dv=- cache=- in=1255 out=26198 meth=GET ref="-" ua="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0" req="GET http://www.google.ca/ HTTP/1.1" dom="google.ca" filetype="-" rule="0" filesize=25815 axtime=0.048193 fttime=0.049360 scantime=0.011 src_cat="0x2f0000002a" labs_cat="0x2f0000002a" dcat_prox="-" target_ip="74.125.127.94" labs_rule_id="0" reqtime=0.027 adtime=0.001625 ftbypass=- os=Windows authn=53 auth_by=portal_cache dnstime=0.000197 quotatime=- sandbox=-
@pytest.mark.addons("sophos")
def test_sophos_webappliance(record_property,  setup_splunk, setup_sc4s):
    host = f"test-sophos-webapp-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{mark}}{{ bsd }} {{ host }} h=10.99.115.13 u="DOMAIN\\johnsmith" s=200 X=- t={{ epoch }} T=284453 Ts=0 act=1 cat="0x220000002a" app="-" rsn=- threat="-" type="text/html" ctype="text/html" sav-ev=4.77 sav-dv=2012.5.10.4770003 uri-dv=- cache=- in=1255 out=26198 meth=GET ref="-" ua="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0" req="GET http://www.google.ca/ HTTP/1.1" dom="google.ca" filetype="-" rule="0" filesize=25815 axtime=0.048193 fttime=0.049360 scantime=0.011 src_cat="0x2f0000002a" labs_cat="0x2f0000002a" dcat_prox="-" target_ip="74.125.127.94" labs_rule_id="0" reqtime=0.027 adtime=0.001625 ftbypass=- os=Windows authn=53 auth_by=portal_cache dnstime=0.000197 quotatime=- sandbox=-\n'
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host, epoch=epoch)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype=sophos:webappliance host="{{ key }}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
