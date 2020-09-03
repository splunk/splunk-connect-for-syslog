import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *
import pytest

env = Environment()


testdata_squid_11_7 = [
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 382 10.0.0.13 TCP_CLIENT_REFRESH_MISS_SSL/201 4646 GET http://test_web.com/page2/b.txt Conner_Fitzerald DEFAULT_PARENT/www.xxxxxxx14.com application/x-javascript OTHER_382-NONE-CyberRange_Inside_NoAuth-OMSPolicy-random_policy-random_policy-DIRECT <IW_swup,ns,-,"-",-,-,-,12,"53AFD.dll",382,382,382,"7EE2C45DB",-,-,"-","-",0,0,IW_swup,"14","-","-","Unknown","-","acbd","aaaaa","ensrch",338.1601,0,[-],"-","-",12,"abcd",382,0,"53AFD.pdf","454A754CA436CA54DB46D101159EAA0EAE6C83D887ED6567165DAB61BD0AF931",-,-,"BlockedFileType:application/x-rpm,BlockedFile:allfiles/linuxpackage.rp",-> "Anonymous_Suspect_Vendor" "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52" - -',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 331 10.0.0.12 TCP_DENIED/403 3197 POST http://test_web.net/contents/content5.jpg Tom_Lawrence DIRECT/www.xxxxxxx7.com application/x-javascript DEFAULT_CASE_331-Auth-APJC_Cisco_Corporate-OMSPolicy-DefaultGroup-NONE-DefaultRouting <nc,9.2,-,"-",-,-,-,25,"3DF63.exe",331,331,331,"C4F04EAD6",-,-,"-","-",0,0,nc,"0","Spyware","threat1","Avc_app","-","Avc_app_category","dbca","unsupp",286.3361,1,[-],"-","-",25,"abcd",331,1,"3DF63.pdf","BA55C3592446ECD7E7B9B28BDCB331DEB76E2AD7ADA164CEB86E7B292965ECA8",-,1,"BlockedFileType:application/x-rpm,BlockedFile:allfiles/linuxpackage.rp",-> "Anonymous_Suspect_Vendor" "Mozilla/5.0 (X11; U; Linux arm7tdmi; rv:1.8.1.11) Gecko/20071130 Minimo/0.025" - -',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 252 10.0.0.2 NONE/504 3040 GET http://test_web.net/users/user5.jpg Tom_Lawrence DIRECT/www.xxxxxxx5.com application/pkix-crl PASSTHRU_ADMIN_252-Decrypt_VFS-WebxOnly-RFS_Transparent_Proxy_Test-random_policy-NONE-DefaultRouting <nc,6.5,-,"-",-,-,-,21,"86196.zip",252,252,252,"8EF1DA258",-,-,"-","-",1,1,nc,"1","Trojan_Phisher","-","ccccc","-","acbd","Unknown","err",343.3854,1,[-],"-","-",21,"-",252,1,"86196.pdf","96AE9C50AFE87221D03802D2B8DC81616D0CA722D4857057DDD40FF32ABB66A8",-,1,"BlockedFileType:application/x-rpm,BlockedFile:allfiles/linuxpackage.rp",-> "abcd" "Mozilla/5.0 (X11; U; Linux arm7tdmi; rv:1.8.1.11) Gecko/20071130 Minimo/0.025" - -',
]

testdata_l4tm = [
    "{{ mark }}{{ bsd }} {{ host }} Mon May 04 12:59:59 2020 Info: Firewall noted TCP data from 10.0.0.15 to 61.79.37.205(www.xxxxxxx7.com):1283.",
    "{{ mark }}{{ bsd }} {{ host }} 04 May 2020 12:59:57 (GMT-1:00) Info: Address 143.164.34.50 discovered for www.xxxxxxx4.com (www.xxxxxxx4.com) added to firewall greylist.",
    "{{ mark }}{{ bsd }} {{ host }} Mon May 04 12:59:54 2020 Info: Begin Logfile",
    "{{ mark }}{{ bsd }} {{ host }} Mon May 04 12:59:49 2020 Info: Version: 9.0.0-485 SN: 848F69E6010F-JYFZWQ1",
    "{{ mark }}{{ bsd }} {{ host }} 04 May 2020 12:59:59 (GMT+5:00) Info: Firewall blocked TCP data from 10.0.0.3:1148 to 96.246.56.182.",
    "{{ mark }}{{ bsd }} {{ host }} Mon May 04 12:59:58 2020 Info: Time offset from UTC: 113 seconds",
]
testdata_squid = [
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 184 10.0.0.6 TCP_CLIENT_REFRESH_MISS/404 461 POST http://test_web.net/users/user2.jpg - DEFAULT_PARENT/www.xxxxxxx15.com application/javascript DEFAULT_CASE_184-NONE-CyberRange_DC_NoAuth-RFS_Transparent_Proxy_Test-random_policy-DefaultGroup-RoutingPolicy <IW_infr,9.2,-,"-",-,-,-,12,"AC238.zip",184,184,184,"3655277AA",-,-,"-","-",0,0,IW_infr,"0","-","-","ccccc","acbd","Avc_app_behaviour","ensrch",331.2241,0,[Remote],"-","-",12,"xyz",184,0,"AC238.pdf","ACC2BCCC5C0D035F7F09CE2DA65472714BAFF0FF5FBC20DA85F00A6CCF3B986C"> "abcd" 486',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 258 10.0.0.12 TCP_MISS/200 4687 GET http://test_web.net/users/user2.jpg Tom_Lawrence DIRECT/www.xxxxxxx15.com image/gif BLOCK_AMW_RESP_URL_258-Allow_All_iDevices-APJC_Cisco_Corporate-RFS_Transparent_Proxy_Test-NONE-random_policy-random_policy <IW_swup,4.5,258,"Trojan-Phisher-Gamec",258,4687,4687,-,"-",-,-,-,"-",-,-,"-","-",-,-,IW_swup,"14","-","-","abcd","bbbbb","aaaaa","err",239.1677,0,[Remote],"-","-",34,"-",258,0,"-","-"> "random_name"',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 17 10.0.0.5 TCP_CLIENT_REFRESH_MISS_SSL/200 1939 HEAD http://test_web.net/contents/content4.jpg - NONE/www.xxxxxxx15.com application/javascript ALLOW_WBRS_17-AccessPolicy-CyberRange_Inside_NoAuth-RFS_Transparent_Proxy_Test-DefaultGroup-random_policy-RoutingPolicy <nc,0.5,-,"-",-,-,-,-,"-",-,-,-,"-",17,17,"C7BFE.zip","89A408E",1,1,nc,14,"-","-","abcd","Unknown","Avc_app_behaviour","err",294.6054,0,[Local],"-","-",37,"-",17,0,"-","-"> - 486',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 245 2001:b8f9:c5c2:f730::2 TCP_DENIED/403 0 GET http://test_web.net/users/user1.jpg Alexei_Romanov NONE/www.xxxxxxx6.com application/x-javascript BLOCK_WEBCAT_245-Allow_All_iDevices-CyberRange_Inside_NoAuth-OMSPolicy-DataSecurityPolicy-DefaultGroup-DIRECT <IW_swup,9.2,-,"-",-,-,-,-,"-",-,-,-,"-",-,-,"-","-",-,-,IW_swup,-,"-","-","Unknown","Unknown","-","-",0.00,0,-,"-","-",-,"-",-,-,"-","-"> -',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 26 2001:44c4:cf35:1b78::6 TCP_MISS/204 4525 POST http://test_web.com/page1/a.txt Andy_Lloyd DIRECT/www.xxxxxxx3.com image/jpeg DEFAULT_CASE_26-NONE-CyberRange_Inside_NoAuth-OMSPolicy-DataSecurityPolicy-ExternalDLPolicy-RoutingPolicy <nc,3.0,-,"-",-,-,-,-,"-",-,-,-,"-",26,26,"1972E.zip","328CD5B",0,0,nc,10,"-","-","Avc_app","acbd","Unknown","ensrch",285.3799,1,[Local],"-","-",27,"-",26,1,"-","-"> "Anonymous_Suspect_Vendor" 100',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 6 10.0.0.7 TCP_CLIENT_REFRESH_MISS/404 1932 GET http://test_web.com/page2/b.txt - DEFAULT_PARENT/www.xxxxxxx8.com - DEFAULT_CASE_6-AP_Subnet_2-NONE-RFS_Transparent_Proxy_Test-NONE-ExternalDLPolicy-RoutingPolicy &lt;nc,5.0,-,"-",-,-,-,-,"-",-,-,-,"-",-,-,"-","-",-,-,nc,-,"-","-","Unknown","Unknown","-","-",0.63,0,-,"-","-",-,"-",-,-,"-","-"&gt; - "03/Jan/2015:07:09:50 +1100" NONE -',
    '{{ mark }}{{ bsd }} {{ host }} {{ wsatime }} 262 10.0.0.7 TCP_MISS_SSL/204 953 POST http://test_web.net/contents/content3.jpg Alexei_Romanov NONE/www.xxxxxxx10.com application/x-javascript DEFAULT_CASE_262-Internet_Access_with_Streaming-ID.ACMETECHISE-NONE-DefaultGroup-random_policy-RoutingPolicy <IW_infr,0.5,-,"-",-,-,-,20,"D4899.rar",262,262,262,"A57EEFA4D",-,-,"-","-",0,0,IW_infr,"13","-","-","Unknown","Unknown","aaaaa","-",229.7138,1,[Remote],"-","-"> "Anonymous_Suspect_Vendor" 123 "07/052020:11:29:10 +1332" NONE "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US) AppleWebKit/125.4 (KHTML, like Gecko, Safari) OmniWeb/v563.15"',
]


@pytest.mark.parametrize("event", testdata_squid_11_7)
def test_cisco_wsa_squid_11_7(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "cisco-wsa11-7-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    wsatime = dt.strftime("%s.%f")[:-3]

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host, wsatime=wsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netproxy _time={{ epoch }} sourcetype="cisco:wsa:squid:new" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", host="", wsatime=wsatime)
    search = st.render(
        epoch=epoch, host=host, message=message1.lstrip().replace('"', '\\"')
    )
    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_squid)
def test_cisco_wsa_squid(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "cisco-wsa-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    wsatime = dt.strftime("%s.%f")[:-3]

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host, wsatime=wsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netproxy _time={{ epoch }} sourcetype="cisco:wsa:squid" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", host="", wsatime=wsatime)
    search = st.render(
        epoch=epoch, host=host, message=message1.lstrip().replace('"', '\\"')
    )
    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_l4tm)
def test_cisco_wsa_l4tm(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "cisco-wsa-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netproxy _time={{ epoch }} sourcetype="cisco:wsa:l4tm" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="")
    search = st.render(epoch=epoch, host=host, message=message1.lstrip())

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
