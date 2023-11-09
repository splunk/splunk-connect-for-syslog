# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
from pytest import mark

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <190>Jan 28 01:28:35 PA-VM300-goran1 1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,1,2014/01/28 01:28:34,192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0


@mark.addons("paloalto")
def test_palo_alto_traffic(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},007200001056,TRAFFIC,end,1210,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,ssl,vsys1,trust-users,untrust,ethernet1/2.30,ethernet1/1,To-Panorama,2020/10/09 17:43:54,36459,1,39681,443,32326,443,0x400053,tcp,allow,43135,24629,18506,189,2020/10/09 16:53:27,3012,sales-laptops,0,1353226782,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,90,99,tcp-fin,16,0,0,0,,{{ host }},from-policy,,,0,,0,,N/A,0,0,0,0,ace432fe-a9f2-5a1e-327a-91fdce0077da,0\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pan:traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Oct 30 09:46:12 1,2012/10/30 09:46:12,01606001116,TRAFFIC,start,1,2012/04/10 04:39:58,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:59,11449,1,59324,80,0,0,0x200000,tcp,allow,78,78,0,1,2012/04/10 04:39:59,0,any,0,0,0x0,192.168.0.0-192.168.255.255,United States,0,1,0
@mark.addons("paloalto")
def test_palo_alto_traffic_dvc_name(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }}-no 1,{{ time }},007200C01056,TRAFFIC,start,1,{{ time }},192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,{{ time }},11449,1,59324,80,0,0,0x200000,tcp,allow,78,78,0,1,2012/04/10 04:39:59,0,any,0,0,0x0,192.168.0.0-192.168.255.255,United States,0,1,0,unknown,dg1,dg2,dg3,dg4,vsys_n13,{{ host }},action_source,src_vm,dest_vm,tunnel_id,tunnel_monitor_tag,tunnel_session_id,tunnel_start_time,tunnel_type\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pan:traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Oct 30 09:46:17 1,2012/10/30 09:46:17,01606001116,THREAT,url,1,2012/04/10 04:39:55,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,"litetopdetect.cn/index.php",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html
@mark.addons("paloalto")
def test_palo_alto_threat(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},01606001116,THREAT,url,1,{{ time }},10.154.7.14,65.55.17.25,,,General Web Infrastructure,pancademo\david.poster,,web-browsing,vsys1,L3-TAP,L3-TAP,ethernet1/2,ethernet1/2,ToUS1RAMA,2017/05/30 00:07:24,661375,1,1058,80,0,0,0xb000,tcp,deny,"emam.firefoxupdata.com/",(9999),malware-sites,informational,client-to-server,899904602,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,text/html,0,,,1,Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB6; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; InfoPath.1; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022),,,,,,,0,31,12,0,0,,{{ host }},,,,get,0,,0,,N/A,unknown,AppThreat-0-0,0x0\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="pan:threat"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Jan 28 01:28:35 fooooo 1,2020/07/08 16:48:50,013201020735,THREAT,url,2049,2020/07/08 16:48:48,10.1.1.1,1.1.1.2,1.1.1.1,1.1.1.3,URLFilter_CatchAll_Internet,testuser,,arcgis,vsys1,DMZ,Outside,ae3,ae1,Panorama-Only,2020/07/08 16:48:48,357728,1,61066,80,33396,80,0x8403000,tcp,alert,"geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?distance=100&f=json&location={""x"":-33,""y"":22.3,""spatialReference"":{""wkid"":111}}",(9999),ALL-WhitelistedURLs,informational,client-to-server,6816029286804555581,0xa000000000000000,Internal,United States,0,application/json,0,,,1,,,,,,,,0,11,16,0,0,,TESTFW01,,,,get,0,,0,,N/A,unknown,AppThreat-0-0,0x0,0,4294967295,
@mark.addons("paloalto")
def test_palo_alto_threat2(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},01606001116,THREAT,url,1,{{ time }},10.154.7.14,65.55.17.25,,,General Web Infrastructure,pancademo\david.poster,,web-browsing,vsys1,L3-TAP,L3-TAP,ethernet1/2,ethernet1/2,ToUS1RAMA,2017/05/30 00:07:24,661375,1,1058,80,0,0,0xb000,tcp,deny,"emam.firefoxupdata.com/",(9999),malware-sites,informational,client-to-server,899904602,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,text/html,0,,,1,Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB6; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; InfoPath.1; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022),,,,,,,0,31,12,0,0,,{{ host }},,,,get,0,,0,,N/A,unknown,AppThreat-0-0,0x0\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="pan:threat"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <14>1 2020-10-09T18:39:02-04:00 paloietf.com - - - - 1,2020/10/09 17:43:54,007200001056,TRAFFIC,end,1210,2020/10/09 17:43:54,10.10.30.69,13.249.117.12,12.235.174.210,13.249.117.12,allow-all,,,ssl,vsys1,trust-users,untrust,ethernet1/2.30,ethernet1/1,To-Panorama,2020/10/09 17:43:54,36459,1,39681,443,32326,443,0x400053,tcp,allow,43135,24629,18506,189,2020/10/09 16:53:27,3012,sales-laptops,0,1353226782,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,90,99,tcp-fin,16,0,0,0,,dvc_name,from-policy,,,0,,0,,N/A,0,0,0,0,ace432fe-a9f2-5a1e-327a-91fdce0077da,0
@mark.addons("paloalto")
def test_palo_alto_traffic_5424(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, _, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} - - - - 1,{{ time }},007200001056,TRAFFIC,end,1210,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,ssl,vsys1,trust-users,untrust,ethernet1/2.30,ethernet1/1,To-Panorama,2020/10/09 17:43:54,36459,1,39681,443,32326,443,0x400053,tcp,allow,43135,24629,18506,189,2020/10/09 16:53:27,3012,sales-laptops,0,1353226782,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,90,99,tcp-fin,16,0,0,0,,{{ host }},from-policy,,,0,,0,,N/A,0,0,0,0,ace432fe-a9f2-5a1e-327a-91fdce0077da,0\n"
    )
    message = mt.render(mark="<14>", iso=iso, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pan:traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@mark.addons("paloalto")
def test_palo_alto_traffic_mstime(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},007200001056,TRAFFIC,end,1210,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,ssl,vsys1,trust-users,untrust,ethernet1/2.30,ethernet1/1,To-Panorama,2020/10/09 17:43:54,36459,1,39681,443,32326,443,0x400053,tcp,allow,43135,24629,18506,189,2020/10/09 16:53:27,3012,sales-laptops,0,1353226782,0x8000000000000000,10.0.0.0-10.255.255.255,United States,0,90,99,tcp-fin,16,0,0,0,,{{ host }},from-policy,,,0,,0,,N/A,0,0,0,0,ace432fe-a9f2-5a1e-327a-91fdce0077da,0\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pan:traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <14>May 11 10:13:22 xxxxxx 1,2020/05/11 10:13:22,015451000001111,HIPMATCH,0,2049,2020/05/11 10:13:22,xx.xx,vsys1,xx-xxxxx-MB,Mac,10.252.31.187,GP-HIP,1,profile,0,0,1052623,0x0,17,11,12,0,,xxxxx,1,0.0.0.0,
@mark.addons("paloalto")
def test_palo_alto_hipmatch(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},015451000001111,HIPMATCH,0,2049,{{ time }},xxxx.xxx,vsys1,xx-xxxxxx-MB,Mac,10.252.31.187,GP-HIP,1,profile,0,0,1052623,0x0,17,11,12,0,,{{ host }},1,0.0.0.0,\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epintel host="{{ host }}" sourcetype="pan:hipmatch"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@mark.addons("paloalto")
def test_palo_alto_globalprotect(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},012001006066,GLOBALPROTECT,0,2305,{{ time }},,gateway-hip-report,host-info,,,user,,SysAdmin,76.1.1.1,0.0.0.0,10.1.15.252,0.0.0.0,f8:ff:c2:47:4c:73,C02ZV00YP4G2,5.0.8,,"",1,,,"",success,,0,,0,opo-mgm-portal,93939,0x8000000000000000'
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pan:globalprotect"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Jan 23 00:45:02 panw-system-host 1,2021/01/23 00:45:03,012001003714,SYSTEM,userid,0,2021/01/22 18:00:10,,connect-ldap-sever-failure,xxx.xxx.xxx.109,0,0,general,medium,"ldap cfg blue-uxxxx-ldap-gm failed to connect to server xxx.xxx.xxx.109 xxx.xxx.xxx.xxx connect to xxx.xxx.xxx.xxx(xxx.xxx.xxx.xxx):636",6837908,0x8000000000000000,0,0,0,0,,XXX_UK_GLA_PAXXX
@mark.addons("paloalto")
def test_palo_alto_system(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},012001006066,SYSTEM,USERID,0,{{ time }},,connect-ldap-sever-failure,xxx.xxx.xxx.109,0,0,general,medium,"ldap cfg blue-uxxxx-ldap-gm failed to connect to server xxx.xxx.xxx.109 xxx.xxx.xxx.xxx connect to xxx.xxx.xxx.xxx(xxx.xxx.xxx.xxx):636",6837908,0x8000000000000000,0,0,0,0,,{{ host }}'
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="pan:system"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Jan 23 00:45:02 panw-system-host 1,2021/01/23 00:45:03,012001003714,SYSTEM,userid,0,2021/01/22 18:00:10,,connect-ldap-sever-failure,xxx.xxx.xxx.109,0,0,general,medium,"ldap cfg blue-uxxxx-ldap-gm failed to connect to server xxx.xxx.xxx.109 xxx.xxx.xxx.xxx connect to xxx.xxx.xxx.xxx(xxx.xxx.xxx.xxx):636",6837908,0x8000000000000000,0,0,0,0,,XXX_UK_GLA_PAXXX
@mark.addons("paloalto")
def test_palo_alto_system_futureproof(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},012001006066,SYSTEM,USERID,0,{{ time }},,connect-ldap-sever-failure,xxx.xxx.xxx.109,0,0,general,medium,"ldap cfg blue-uxxxx-ldap-gm failed to connect to server xxx.xxx.xxx.109 xxx.xxx.xxx.xxx connect to xxx.xxx.xxx.xxx(xxx.xxx.xxx.xxx):636",6837908,0x8000000000000000,0,0,0,0,,{{ host }},something'
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="pan:system"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
