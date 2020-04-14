# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest
env = Environment()


#Jan 17 03:35:18 SV5-F5-5600-2.splunk.com notice tmsh[16322]: 01420002:5: AUDIT - pid=16322 user=root folder=/ module=(tmos)# status=[Command OK] cmd_data=cd / ;
#Jan 17 09:44:14 SV5-F5-5600-2.splunk.com info httpd(pam_audit)[16784]: 01070417:6: AUDIT - user aesguerra - RAW: httpd(pam_audit): user=aesguerra(aesguerra) partition=[All] level=Administrator tty=(unknown) host=10.77.112.22 attempts=1 start=""Fri Jan 17 09:44:10 2020"" end=""Fri Jan 17 09:44:14 2020"".
#Jan 17 09:52:46 SV5-F5-5600-2.splunk.com info sshd(pam_audit)[21398]: 01070417:6: AUDIT - user aesguerra - RAW: sshd(pam_audit): user=aesguerra(aesguerra) partition=[All] level=Administrator tty=ssh host=10.77.112.22 attempts=1 start="Fri Jan 17 09:52:46 2020".
#Jan 17 03:35:04 SV5-F5-5600-2.splunk.com info audit_forwarder[16218]: audit_forwarder started.
#Jan 17 03:35:35 SV5-F5-5600-2.splunk.com info systemd-journal[626]: Suppressed 1255 messages from /system.slice/runit.service
#Jan 17 03:37:54 SV5-F5-5600-2 warning tmm[23068]: 01260013:4: SSL Handshake failed for TCP 10.160.23.133:50365 -> 10.156.1.150:443
#Jan 17 03:38:00 SV5-F5-5600-2 err tmm[23068]: 01220001:3: TCL error: /Common/stg-Artifactory-iRule <HTTP_REQUEST> - ERR_NOT_SUPPORTED (line 8)     invoked from within "HTTP::method"
#Jan 17 04:03:37 SV5-F5-5600-2 warning tmm1[23068]: 01260009:4: Connection error: ssl_passthru:5234: not SSL (40)
#Jan 17 04:42:37 SV5-F5-5600-2.splunk.com notice mcpd[10653]: 01070638:5: Pool /Common/infra-docs-pool member /Common/go_web3:4000 monitor status down. [ /Common/tcp_half_open: down; last error:  ]  [ was up for 837hrs:31mins:36sec ]
#Jan 17 04:42:37 SV5-F5-5600-2 notice apmd[11023]: 01490248:5: /Common/Network_Access_02:Common:8c6be305: Received client info - Hostname:  Type: IE Version: 8 Platform: Win7 CPU: WOW64 UI Mode: Full Javascript Support: 1 ActiveX Support: 1 Plugin Support: 0
#2019-12-12T15:54:12.972208-08:00 10.160.21.242,f5_irule=Splunk-HSL-iRule-HTTP,src_ip=10.32.30.21,vip=10.156.1.160,http_method=GET,http_host=confluence.splunk.com: 443,http_uri=/download/attachments/185799227/Dynamic%20Lookups%20in%20RZ%20-%20architecture.png?version=1&modificationDate=1574471645759&api=v2,http_url=confluence.splunk.com:443/download/attachments/185799227/Dynamic%20Lookups%20in%20RZ%20-%20architecture.png?version=1&modificationDate=1574471645759&api=v2,http_version=1.1,http_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",http_content_type=,http_referrer="https://confluence.splunk.com/display/SEC/Dynamic+Lookups+in+RZ",req_start_time=2019/12/12 15:54:12,cookie="optimizelyBuckets _ga __ktt _gid optimizelyEndUserId __lc.visitor_id.3988321 _cs_c SPLUNK_SUB_LOGIN confluence.list.pages.cookie __kti __ktv _gcl_au crowd.token_key __utmv SPLUNK_USER_LOGIN_STATUS OptanonConsent trackAffiliate lc_sso3988321 _fbp _fbc confluence.browse.space.cookie _biz_pendingA ELOQUA __utmz ajs_group_id SPLUNK_SUB_SIGNUP _biz_nA _cs_id _hjid __utma mywork.tab.tasks optimizelySegments __utmc SPLUNK_AFFILIATE_CODE JSESSIONID Apache _biz_uid distance ajs_anonymous_id _biz_flagsA _st _gaexp __kts",user=,virtual_server="/Common/confluence-pool 10.156.18.12 8090",bytes_in=0,res_start_time=2019/12/12 15:54:12,node=10.156.18.12,node_port=8090,http_status=200,req_elapsed_time=21,bytes_out=75366#015

testdata_nix = [
'{{ mark }}{{ bsd }} {{ host }} info httpd(pam_audit)[16784]: 01070417:6: AUDIT - user aesguerra - RAW: httpd(pam_audit): user=aesguerra(aesguerra) partition=[All] level=Administrator tty=(unknown) host=10.77.112.22 attempts=1 start="Fri Jan 17 09:44:10 2020" end="Fri Jan 17 09:44:14 2020".',
'{{ mark }}{{ bsd }} {{ host }} info sshd(pam_audit)[21398]: 01070417:6: AUDIT - user aesguerra - RAW: sshd(pam_audit): user=aesguerra(aesguerra) partition=[All] level=Administrator tty=ssh host=10.77.112.22 attempts=1 start="Fri Jan 17 09:52:46 2020".',
'{{ mark }}{{ bsd }} {{ host }} info audit_forwarder[16218]: audit_forwarder started.',
'{{ mark }}{{ bsd }} {{ host }} info systemd-journal[626]: Suppressed 1255 messages from /system.slice/runit.service',
]

testdata_app = [
'{{ mark }}{{ bsd }} {{ host }} notice tmsh[16322]: 01420002:5: AUDIT - pid=16322 user=root folder=/ module=(tmos)# status=[Command OK] cmd_data=cd / ;',
'{{ mark }}{{ bsd }} {{ host }} warning tmm[23068]: 01260013:4: SSL Handshake failed for TCP 10.160.23.133:50365 -> 10.156.1.150:443',
'{{ mark }}{{ bsd }} {{ host }} err tmm[23068]: 01220001:3: TCL error: /Common/stg-Artifactory-iRule <HTTP_REQUEST> - ERR_NOT_SUPPORTED (line 8)     invoked from within "HTTP::method"',
'{{ mark }}{{ bsd }} {{ host }} warning tmm1[23068]: 01260009:4: Connection error: ssl_passthru:5234: not SSL (40)',
'{{ mark }}{{ bsd }} {{ host }} notice mcpd[10653]: 01070638:5: Pool /Common/infra-docs-pool member /Common/go_web3:4000 monitor status down. [ /Common/tcp_half_open: down; last error:  ]  [ was up for 837hrs:31mins:36sec ]',
'{{ mark }}{{ bsd }} {{ host }} notice apmd[11023]: 01490248:5: /Common/Network_Access_02:Common:8c6be305: Received client info - Hostname:  Type: IE Version: 8 Platform: Win7 CPU: WOW64 UI Mode: Full Javascript Support: 1 ActiveX Support: 1 Plugin Support: 0',
]
testdata_irule = [
'{{ mark }}{{ iso }} {{ host }},f5_irule=Splunk-HSL-iRule-HTTP,src_ip=10.111.30.21,vip=10.1111.1.160,http_method=GET,http_host=confluence.splunk.com: 443,http_uri=/download/attachments/185799227/Dynamic%20Lookups%20in%20RZ%20-%20architecture.png?version=1&modificationDate=1574471645759&api=v2,http_url=confluence.splunk.com:443/download/attachments/185799227/Dynamic%20Lookups%20in%20RZ%20-%20architecture.png?version=1&modificationDate=1574471645759&api=v2,http_version=1.1,http_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",http_content_type=,http_referrer="https://confluence.splunk.com/display/SEC/Dynamic+Lookups+in+RZ",req_start_time=2019/12/12 15:54:12,cookie="optimizelyBuckets _ga __ktt _gid optimizelyEndUserId __lc.visitor_id.3988321 _cs_c SPLUNK_SUB_LOGIN confluence.list.pages.cookie __kti __ktv _gcl_au crowd.token_key __utmv SPLUNK_USER_LOGIN_STATUS OptanonConsent trackAffiliate lc_sso3988321 _fbp _fbc confluence.browse.space.cookie _biz_pendingA ELOQUA __utmz ajs_group_id SPLUNK_SUB_SIGNUP _biz_nA _cs_id _hjid __utma mywork.tab.tasks optimizelySegments __utmc SPLUNK_AFFILIATE_CODE JSESSIONID Apache _biz_uid distance ajs_anonymous_id _biz_flagsA _st _gaexp __kts",user=,virtual_server="/Common/confluence-pool 10.156.18.12 8090",bytes_in=0,res_start_time=2019/12/12 15:54:12,node=10.156.18.12,node_port=8090,http_status=200,req_elapsed_time=21,bytes_out=75366#015'
]
@pytest.mark.parametrize("event", testdata_nix)
def test_f5_bigip_nix(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = "test_f5-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"nix:syslog\" host=\"{{ host }}\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@pytest.mark.parametrize("event", testdata_app)
def test_f5_bigip_app(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = "test_f5-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"f5:bigip:syslog\" host=\"{{ host }}\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_irule)
def test_f5_bigip_irule(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = "test_f5-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"f5:bigip:irule\" host=\"{{ host }}\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@pytest.mark.parametrize("event", testdata_app)
def test_f5_bigip_app_default(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"f5:bigip:syslog\" host=\"{{ host }}\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_irule)
def test_f5_bigip_irule_default(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

     # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search index=netops _time={{ epoch }} sourcetype=\"f5:bigip:irule\" host=\"{{ host }}\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <141>1 2020-04-14T14:39:05.271965+00:00 f5-bigip.com apmd 7389 01490248:5: [F5@12276 hostname="f5-bigip.com" errdefs_msgno="01490248:5:" partition_name="RAS" session_id="7a7860e5" Access_Profile="/RAS/BSP-Prod-200407" Partition="RAS" Session_ID="7a7860e5" Client_Hostname="PFF-client" Client_Type="Standalone" Client_Version="2.0" Client_Platform="Win10" Client_CPU="WOW64" Client_UI_Mode="Standalone" Client_JS_Support="1" Client_Activex_Support="1" Client_Plugin_Support="0"] /RAS/BSP-Prod-200407:ras:a7860e5: Received client info - Hostname: PFF-client Type: Standalone Version: 2.0 Platform: Win10 CPU: WOW64 UI Mode: Standalone Javascript Support: 1 ActiveX Support: 1 Plugin Support: 0# @pytest.mark.xfail
def test_f5_bigip_app_structured(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }} {{ host }} apmd 7389 01490248:5: [F5@12276 hostname=\"f5-bigip.com\" errdefs_msgno=\"01490248:5:\" partition_name=\"RAS\" session_id=\"7a7860e5\" Access_Profile=\"/RAS/BSP-Prod-200407\" Partition=\"RAS\" Session_ID=\"7a7860e5\" Client_Hostname=\"PFF-client\" Client_Type=\"Standalone\" Client_Version=\"2.0\" Client_Platform=\"Win10\" Client_CPU=\"WOW64\" Client_UI_Mode=\"Standalone\" Client_JS_Support=\"1\" Client_Activex_Support=\"1\" Client_Plugin_Support=\"0\"] /RAS/BSP-Prod-200407:ras:a7860e5: Received client info - Hostname: PFF-client Type: Standalone Version: 2.0 Platform: Win10 CPU: WOW64 UI Mode: Standalone Javascript Support: 1 ActiveX Support: 1 Plugin Support: 0# @pytest.mark.xfail\n")
    message = mt.render(mark="<141>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netops host=\"{{ host }}\" sourcetype=\"f5:bigip:syslog\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
