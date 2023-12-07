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

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Nov 15 23:57:28 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|13.5.0.10_0|Custom|custom-policy-violation|High|act=block dst=1.1.1.1 dpt=80 duser=GeritaMija3s src=1.0.0.1 spt=59774 proto=TCP rt=Nov 15 2019 15:52:28 cat=Alert cs1=Suspicious File Access Attempt - 1 cs1Label=Policy cs2=WebCloud (simulation) cs2Label=ServerGroup cs3=WebCloud HTTP Service (simulation) cs3Label=ServiceName cs4=english.hku.hk Application cs4Label=ApplicationName cs5=custom-policy-violation cs5Label=Description cs6=POST cs6Label=HTTPHeaderRequest-URLMethod cs7=/uploads/dede/sys_verifies.php cs7Label=HTTPHeaderRequest-URLPath cs8=Connection, Content-Type, Accept, Referer, User-Agent, Content-Length, Host Keep-Alive, application/x-www-form-urlencoded, */*, http://aaaaa.bbb.cc/uploads/dede/sys_verifies.php?action=down, Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2), 231, english.hku.hk cs8Label=HttpHeaderRequest-Header cs9=down action cs9Label=HttpHeaderRequest-Parameters cs10=6704543119945989736 cs10Label=EventID cs11=7500662780438769543 cs11Label=SessionID
# Nov 15 23:45:44 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|13.5.0.10_0|Correlation|sql-injection|High|act=block dst=1.1.1.1 dpt=80 duser=Marcelavms src=1.0.0.1 spt=46814 proto=TCP rt=Nov 15 2019 15:45:42 cat=Alert cs1=Web Correlation Policy cs1Label=Policy cs2=AAA Wildcard (Dept) (simulation cs2Label=ServerGroup cs3=AAA Wildcard (Dept) HTTP Service (simulation) cs3Label=ServiceName cs4=aaa.bbb.hk Application cs4Label=ApplicationName cs5=sql-injection cs5Label=Description cs6=GET cs6Label=HTTPHeaderRequest-URLMethod cs7=/cdblog/wp-trackback.php cs7Label=HTTPHeaderRequest-URLPath cs8=Accept-Language, Accept-Charset, Accept, User-Agent, Host, Connection en-us,en, utf-8,*, text/html,image/jpeg,image/gif,text/xml,text/plain,image/png, Opera/9.27, aaa.bbb.hk, close cs8Label=HttpHeaderRequest-Header cs9=555&&BeNChMaRK(2999999,MD5(NOW())) p cs9Label=HttpHeaderRequest-Parameters cs10=6704543119945954386 cs10Label=EventID cs11= cs11Label=SessionID
test_fallback_events = [
    "{{ mark }} {{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|13.5.0.10_0|Custom|custom-policy-violation|High|act=block dst=1.1.1.1 dpt=80 duser=GeritaMija3s src=1.0.0.1 spt=59774 proto=TCP rt={{ bsd }} cat=Alert cs1=Suspicious File Access Attempt - 1 cs1Label=Policy cs2=WebCloud (simulation) cs2Label=ServerGroup cs3=WebCloud HTTP Service (simulation) cs3Label=ServiceName cs4=aaaa.bbb.cc Application cs4Label=ApplicationName cs5=custom-policy-violation cs5Label=Description cs6=POST cs6Label=HTTPHeaderRequest-URLMethod cs7=/uploads/dede/sys_verifies.php cs7Label=HTTPHeaderRequest-URLPath cs8=Connection, Content-Type, Accept, Referer, User-Agent, Content-Length, Host Keep-Alive, application/x-www-form-urlencoded, */*, http://aaaaa.bbb.cc/uploads/dede/sys_verifies.php?action=down, Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2), 231, aaaa.bbb.cc cs8Label=HttpHeaderRequest-Header cs9=down action cs9Label=HttpHeaderRequest-Parameters cs10=6704543119945989736 cs10Label=EventID cs11=7500662780438769543 cs11Label=SessionID",
    "{{ mark }} {{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|13.5.0.10_0|Correlation|sql-injection|High|act=block dst=1.1.1.1 dpt=80 duser=Marcelavms src=1.0.0.1 spt=46814 proto=TCP rt={{ bsd }} cat=Alert cs1=Web Correlation Policy cs1Label=Policy cs2=AAA Wildcard (Dept) (simulation cs2Label=ServerGroup cs3=AAA Wildcard (Dept) HTTP Service (simulation) cs3Label=ServiceName cs4=aaa.bbb.hk Application cs4Label=ApplicationName cs5=sql-injection cs5Label=Description cs6=GET cs6Label=HTTPHeaderRequest-URLMethod cs7=/cdblog/wp-trackback.php cs7Label=HTTPHeaderRequest-URLPath cs8=Accept-Language, Accept-Charset, Accept, User-Agent, Host, Connection en-us,en, utf-8,*, text/html,image/jpeg,image/gif,text/xml,text/plain,image/png, Opera/9.27, aaa.bbb.hk, close cs8Label=HttpHeaderRequest-Header cs9=555&&BeNChMaRK(2999999,MD5(NOW())) p cs9Label=HttpHeaderRequest-Parameters cs10=6704543119945954386 cs10Label=EventID cs11= cs11Label=SessionID",
]

@pytest.mark.addons("imperva")
@pytest.mark.parametrize("event", test_fallback_events)
def test_imperva_waf_fallback(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<11>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="imperva:waf" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Jan 30 14:43:13 146.222.1.43 CEF:0|Imperva Inc.|SecureSphere|13.0.0|Signature|Sql Signature Violation|Low|act=None dst=10.222.17.15 dpt=1521 duser=Multiple src=10.222.17.15 spt=51462 proto=TCP rt=Jan 30 2020 08:43:15 cat=Alert cs1=Recommended Signatures Policy for Database Applications cs1Label=Policy cs2=hklp320p cs2Label=ServerGroup cs3=Multiple EXECUTE IMMEDIATE attempt(+)  from 10.222.17.15 cs3Label=Description
# Jan 30 14:50:39 146.222.1.43 CEF:0|Imperva Inc.|SecureSphere|13.0.0|Protocol|Extremely Long SQL Request|High|act=None dst=146.222.96.180 dpt=0 duser=n/a src=10.222.57.18 spt=46205 proto=TCP rt=Jan 30 2020 04:50:35 cat=Alert cs1=SQL Protocol Policy cs1Label=Policy cs2=hklp743p cs2Label=ServerGroup cs3=hklp743p_oracle cs3Label=ServiceName cs4=Default Oracle Application cs4Label=ApplicationName cs5=Multiple Extremely Long SQL Request from 10.222.57.18 cs5Label=Description
# Jul 16 18:19:52 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|10.5.0|Worm|Web Worm|High|act=Block dst=1.1.1.1 dpt=80 duser=n/a src=1.0.0.1 spt=65535 proto=TCP rt=Jul 16 2015 18:19:50 cat=Alert cs1=Web Worm Policy cs1Label=Policy cs2=Server3 cs2Label=ServerGroup cs3=ServiceName3 cs3Label=ServiceName cs4=ApplicationName3 cs4Label=ApplicationName cs5=Access to: /cgi-system/rtpd.cgi cs5Label=Description
test_security_events = [
    "{{ mark }}{{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|13.0.0|Signature|Sql Signature Violation|Low|act=None dst=10.222.17.15 dpt=1521 duser=Multiple src=10.222.17.15 spt=51462 proto=TCP rt={{ bsd }} cat=Alert cs1=Recommended Signatures Policy for Database Applications cs1Label=Policy cs2=hklp320p cs2Label=ServerGroup cs3=Multiple EXECUTE IMMEDIATE attempt(+)  from 10.222.17.15 cs3Label=Description",
    "{{ mark }}{{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|13.0.0|Protocol|Extremely Long SQL Request|High|act=None dst=146.222.96.180 dpt=0 duser=n/a src=10.222.57.18 spt=46205 proto=TCP rt={{ bsd }} cat=Alert cs1=SQL Protocol Policy cs1Label=Policy cs2=hklp743p cs2Label=ServerGroup cs3=hklp743p_oracle cs3Label=ServiceName cs4=Default Oracle Application cs4Label=ApplicationName cs5=Multiple Extremely Long SQL Request from 10.222.57.18 cs5Label=Description",
    "{{ mark }}{{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|10.5.0|Worm|Web Worm|High|act=Block dst=1.1.1.1 dpt=80 duser=n/a src=1.0.0.1 spt=65535 proto=TCP rt={{ epoch }} cat=Alert cs1=Web Worm Policy cs1Label=Policy cs2=Server3 cs2Label=ServerGroup cs3=ServiceName3 cs3Label=ServiceName cs4=ApplicationName3 cs4Label=ApplicationName cs5=Access to: /cgi-system/rtpd.cgi cs5Label=Description",
]


@pytest.mark.addons("imperva")
@pytest.mark.parametrize("event", test_security_events)
def test_imperva_waf_security(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="imperva:waf:security:cef" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 19 10:29:53 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|12.0.0|Firewall|SSL Untraceable Connection|Medium|act=Block dst=160.131.222.235 dpt=2157 duser=Mathbelliin src=49.93.221.243 spt=11286 proto=TCP rt=Jan 30 2020 14:41:23 cat=Alert cs1=Automated Vulnerability Scanning cs1Label=Policy cs2=IRIS_1 cs2Label=ServerGroup cs3=app1-5.host1.com [Multi_VIP] cs3Label=ServiceName cs4=For Monitor ONLY cs4Label=ApplicationName cs5=Distributed Too Many Headers per Response cs5Label=Description
@pytest.mark.addons("imperva")
def test_imperva_waf_firewall(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Imperva Inc.|SecureSphere|12.0.0|Firewall|SSL Untraceable Connection|Medium|act=Block dst=160.131.222.235 dpt=2157 duser=Mathbelliin src=49.93.221.243 spt=11286 proto=TCP rt={{ bsd }} cat=Alert cs1=Automated Vulnerability Scanning cs1Label=Policy cs2=IRIS_1 cs2Label=ServerGroup cs3=app1-5.host1.com [Multi_VIP] cs3Label=ServiceName cs4=For Monitor ONLY cs4Label=ApplicationName cs5=Distributed Too Many Headers per Response cs5Label=Description"
    )
    message = mt.render(bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netwaf _time={{ epoch }} sourcetype="imperva:waf:firewall:cef" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
