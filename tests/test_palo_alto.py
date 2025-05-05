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

def get_panlc_times():
    dt = datetime.datetime.now()
    bsd = dt.strftime("%b %d %H:%M:%S")
    time = dt.strftime("%Y/%m/%d %H:%M:%S")

    # Simulate a delay: 15 minutes
    original_dt = dt - datetime.timedelta(minutes=15)

    # Timezone offset
    offset = datetime.timedelta(hours=-4)
    dt_timezone = (original_dt + offset).replace(tzinfo=datetime.timezone(offset))

    # 2025-04-02T11:57:03.887-04:00
    offset_str = dt_timezone.strftime('%z')
    offset_str = offset_str[:3] + ':' + offset_str[3:] # '-0400' -> '-04:00'
    orig_timestamp_str = dt_timezone.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt_timezone.microsecond // 1000:03d}' + offset_str

    epoch = original_dt.strftime("%s.%f")[:-3]
    return bsd, time, orig_timestamp_str, epoch

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

# <190>Mar 28 05:40:45 system-host 1,2025/03/28 05:34:14,000000000000,TRAFFIC,end,0000,2025/03/28 05:34:14,11.111.11.111,11.111.11.111,11.111.11.111,11.111.11.111,111111-111111,,,windows-defender-atp-endpoint,vsys0,xxxxx-xxx,xxxxx_xx_xxxx,xx11.111,xx11.111,Panorama-log,2025/03/28 05:34:14,1111111,1,11111,1111,0,0,0x111111,tcp,allow,11111,1111,1111,11,2025/03/28 05:33:55,17,url,,1111111111111111111,0x8000000000000000,10.0.0.0-10.255.255.255,Country,,11,11,tcp-xxx,1111,11111,1111,0,XX-XX-XXX-X-000-XXX-XXX,XX-XX-XXX-XX-000X,from-policy,,,0,,0,,N/A,0,0,0,0,000000xx-00x0-000z-00xx-x00x00000000x,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,2025-03-28T05:34:15.104-04:00,,,management,business-systems,client-server,1,has-known-vulnerability,windows-defender-atp,windows-defender-atp-endpoint,no,no,0
@mark.addons("paloalto")
def test_palo_alto_traffic_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},000000000000,TRAFFIC,end,0000,{{ time }},11.111.11.111,11.111.11.111,11.111.11.111,11.111.11.111,111111-111111,,,windows-defender-atp-endpoint,vsys0,xxxxx-xxx,xxxxx_xx_xxxx,xx11.111,xx11.111,Panorama-log,{{ time }},1111111,1,11111,1111,0,0,0x111111,tcp,allow,11111,1111,1111,11,2025/03/28 05:33:55,17,url,,1111111111111111111,0x8000000000000000,10.0.0.0-10.255.255.255,Country,,11,11,tcp-xxx,1111,11111,1111,0,XX-XX-XXX-X-000-XXX-XXX,{{ host }},from-policy,,,0,,0,,N/A,0,0,0,0,000000xx-00x0-000z-00xx-x00x00000000x,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,{{ high_res_time }},,,management,business-systems,client-server,1,has-known-vulnerability,windows-defender-atp,windows-defender-atp-endpoint,no,no,0\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, high_res_time=orig_timestamp_str)

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

# <190>Mar 14 14:28:52 host-name 1,2025/03/14 16:28:52,111111111111111,CONFIG,0,1111,2025/03/14 16:28:40,0.0.0.0,,commit-all,Panorama-admin,Panorama,Succeeded,,1111111111111111111111111,0x8000000000000000,0,0,0,0,,host-name,0,,0,2025-03-14T16:28:40.583+01:00
@mark.addons("paloalto")
def test_palo_alto_config_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},111111111111111,CONFIG,0,1111,{{ time }},0.0.0.0,,commit-all,Panorama-admin,Panorama,Succeeded,,1111111111111111111111111,0x8000000000000000,0,0,0,0,,{{ host }},0,,0,{{ high_res_time }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, high_res_time=orig_timestamp_str)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="pan:config"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# <190>Oct 30 09:46:17 1,2012/10/30 09:46:17,01606001116,THREAT,url,1,2012/04/10 04:39:55,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,"litetopdetect.cn/index.php",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html
@mark.addons("paloalto")
def test_palo_alto_threat_old_format(record_property,  setup_splunk, setup_sc4s):
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
def test_palo_alto_threat_old_format_2(record_property,  setup_splunk, setup_sc4s):
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

# <190>Apr 02 11:57:03 fooooo 1,2025/04/02 11:57:03,000000000000,THREAT,url,2562,2025/04/02 11:57:03,11.11.111.11,11.11.111.111,111.111.11.11,11.11.111.111,WEB-App,user,,web-browsing,vsys2,VCN,Internet,ae1.111,ae2.111,Panorama-log,2025/04/02 11:57:03,111111111,1,64922,443,50525,443,0x140b000,tcp,alert,"subdomain.domain.com/graphql?operationName=getAlertsNews&variables={}&extensions={""persistedQuery"":{""version"":1,""sha256Hash"":""hash""}}",9999(9999),business-and-economy,informational,client-to-server,111111111112221111111111,0x8000000000000000,10.0.0.0-10.255.255.255,Country,,text/html,0,,,29,,,,,,,,0,13,62,2817,0,XX-XX-XXX-X-111-XXX,XX-XX-XXX-XX-111X,,,,options,0,,0,,N/A,N/A,AppThreat-0-0,0x0,0,1111111111111,,"business-and-economy,low-risk",xxxxx-xxxx-xxx-xxx-xxx,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0,2025-04-02T11:57:03.887-04:00,,,,internet-utility,general-internet,browser-based,4,"used-by-malware,able-to-transfer-file,has-known-vulnerability,tunnel-other-application,pervasive-use",,web-browsing,no,no,
@mark.addons("paloalto")
def test_palo_alto_threat_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    """
    If the high-resolution timestamp is available, it should be used instead of the regular timestamp.
    """
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ recv_time }},00000000000,THREAT,url,2562,{{ recv_time }},11.11.111.11,11.11.111.111,111.111.11.11,11.11.111.111,WEB-App,user,,web-browsing,vsys2,VCN,Internet,ae1.111,ae2.111,Panorama-log,{{ recv_time }},111111111,1,64922,443,50525,443,0x140b000,tcp,alert,"subdomain.domain.com/graphql?operationName=getAlertsNews&variables={}&extensions={""persistedQuery"":{""version"":1,""sha256Hash"":""hash""}\}",9999(9999),business-and-economy,informational,client-to-server,111111111112221111111111,0x8000000000000000,10.0.0.0-10.255.255.255,Country,,text/html,0,,,29,,,,,,,,0,13,62,2817,0,XX-XX-XXX-X-111-XXX,{{ host }},,,,options,0,,0,,N/A,N/A,AppThreat-0-0,0x0,0,1111111111111,,"business-and-economy,low-risk",xxxxx-xxxx-xxx-xxx-xxx,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0,{{ high_res_time }},,,,internet-utility,general-internet,browser-based,4,"used-by-malware,able-to-transfer-file,has-known-vulnerability,tunnel-other-application,pervasive-use",,web-browsing,no,no,\n',
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, recv_time=time, high_res_time=orig_timestamp_str)

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

# <190>Mar 28 05:40:45 system-host 1,2025/04/02 17:55:34,1111111111111111111,HIPMATCH,0,1111,2025/04/02 17:55:28,user@mail.com,vsys1,XXXXXXXXXXXXX,Windows,11.111.111.1,HIP-Compliant-Client,1,profile,,,111111111111111111,0x8000000000000000,13,330,29982,0,,XXXXXXXXXXXX,1,0.0.0.0,xxx-xxx-xxx-xxx-xxx,xxxx,,2025-04-02T17:55:28.942+02:00
@mark.addons("paloalto")
def test_palo_alto_hipmatch_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},1111111111111111111,HIPMATCH,0,1111,{{ time }},user@mail.com,vsys1,XXXXXXXXXXXXX,Windows,11.111.111.1,HIP-Compliant-Client,1,profile,,,111111111111111111,0x8000000000000000,13,330,29982,0,,{{ host }},1,0.0.0.0,xxx-xxx-xxx-xxx-xxx,xxxx,,{{ high_res_time }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, high_res_time=orig_timestamp_str)

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
    get_host_name = lambda: f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    orig_host = get_host_name()
    overwritten_host_name = get_host_name()

    dt = datetime.datetime.now()
    _, bsd, time, _, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ orig_host }} 1,{{ time }},XXXXXXXXXXXXXXXXXX,GLOBALPROTECT,0,2561,{{ time }},vsys1,gateway-logout,logout,,,XXXXXXXX,XX,XXXXXXXXXXXXXX,8.8.8.8,0.0.0.0,192.0.0.1,0.0.0.0,XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX,XXXXXXXXXXXX,5.2.12,Windows,"Microsoft Windows 10 Enterprise , 64-bit",1,,,"client logout",success,,1554,,0,XXXXXXXXXXXXXXXXXXXX,XXXXXXXXXXXXXXXX,0x8000000000000000,2023-11-09T16:39:17.223+01:00,,,,,,13,19,52,450,,{{ overwritten_host_name }},1'
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, orig_host=orig_host, time=time, overwritten_host_name=overwritten_host_name)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ overwritten_host_name }} sourcetype="pan:globalprotect"'
    )
    search = st.render(epoch=epoch, overwritten_host_name=overwritten_host_name)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", overwritten_host_name)
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

# <190>Mar 28 05:40:45 system-host 1,2025/03/28 05:40:45,000000000000,USERID,login,0000,2025/03/28 05:40:45,vsys0,11.111.11.111,usr,,0,1,10800,0,0,vpn-client,globalprotect,0000000000000000000,0x8000000000000000,11,11,1111,0,virtual-system-name,device-name,1,,2025/03/28 05:40:45,1,0x0,a111111,,2025-03-28T05:40:45.986-04:00
@mark.addons("paloalto")
def test_palo_alto_userid_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},000000000000,USERID,login,0000,2025/03/28 05:40:45,vsys0,11.111.11.111,usr,,0,1,10800,0,0,vpn-client,globalprotect,0000000000000000000,0x8000000000000000,11,11,1111,0,virtual-system-name,{{ host }},1,,2025/03/28 05:40:45,1,0x0,a111111,,{{ high_res_time }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, high_res_time=orig_timestamp_str)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="pan:userid"'
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


# <14>1 2023-07-06T19:20:22+00:00 DEVICE_NAME 1,{{ time }},007XXXXX341044,DECRYPTION,0,2562,{{ time }},XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,AWS Services by URL - Egress,,,incomplete,vsys1,Default Zone,Default Zone,ethernet1/1,ethernet1/1,ANONYMIZED,{{ time }},504326,1,37612,443,0,0,0x1000000,tcp,allow,N/A,,,,,ANONYMIZED,Server_Hello_Done,Client_Hello,TLS1.2,ECDHE,AES_128_GCM,SHA256,ANONYMIZED,secp256r1,Certificate,trusted,Trusted,Forward,ANONYMIZED,XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,[DATE], [DATE],V3,2048,12,45,34,18,:::::RSA,*.badssl.com,ANONYMIZED,ANONYMIZED,expired.badssl.com,Received fatal alert CertificateExpired from client. CA Issuer URL (truncated):ANONYMIZED,[DATE-TIME],,,,,,,,,,ANONYMIZED,0x8000000000000000,29,82,454,0,,ANONYMIZED,1,unknown,unknown,unknown,1,,,incomplete,no,no
@mark.addons("paloalto")
def test_palo_alto_decryption(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},007XXXXX341044,DECRYPTION,0,2562,{{ time }},XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,XXX.XXX.XXX.XXX,AWS Services by URL - Egress,,,incomplete,vsys1,Default Zone,Default Zone,ethernet1/1,ethernet1/1,ANONYMIZED,{{ time }},504326,1,37612,443,0,0,0x1000000,tcp,allow,N/A,,,,,ANONYMIZED,Server_Hello_Done,Client_Hello,TLS1.2,ECDHE,AES_128_GCM,SHA256,ANONYMIZED,secp256r1,Certificate,trusted,Trusted,Forward,ANONYMIZED,XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,[DATE], [DATE],V3,2048,12,45,34,18,:::::RSA,*.badssl.com,ANONYMIZED,ANONYMIZED,expired.badssl.com,Received fatal alert CertificateExpired from client. CA Issuer URL (truncated):ANONYMIZED,[DATE-TIME],,,,,,,,,,ANONYMIZED,0x8000000000000000,29,82,454,0,,ANONYMIZED,1,unknown,unknown,unknown,1,,,incomplete,no,no\n'
    )
    message = mt.render(mark="<14>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="pan:decryption"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# <190>Mar 28 05:40:45 system-host 1,{{ time }},111111111111111111111,DECRYPTION,0,2562,{{ time }},11.11.111.111,11.11.111.111,11.111.1.11,11.11.111.111,external-access,,,ssl,vsys1,XXX1,Internet,ethernet1/1,ethernet1/2,Log_Forwarding_Profile_XX,{{ time }},111111111,1,1111111,443,38178,443,0x400400,tcp,allow,N/A,,,,,xxxxxx-xxxxx-xxxxx-xxxx-xxxxxxx,Certificate,Certificate,TLS1.2,ECDHE,AES_128_GCM,SHA256,external-access,,None,uninspected,Uninspected,No Decrypt,xxxxx,xxxxxxxx,2025/02/10 15:21:54,2028/02/10 15:21:54,V3,2048,34,27,0,0,:::::RSA,url.com,Intermediate CA,,,,,,,,,,,2025-04-02T15:56:19.287+00:00,,,,,,,,,,,,,,,,,xxx,xxx,20,0,0,0,,xx-xx-firewall-xx,1,encrypted-tunnel,networking,browser-based,4,"used-by-malware,able-to-transfer-file,has-known-vulnerability,tunnel-other-application,pervasive-use",,ssl,no,no
@mark.addons("paloalto")
def test_palo_alto_decryption_high_resolution_timestamp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    bsd, time, orig_timestamp_str, epoch = get_panlc_times()

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},111111111111111111111,DECRYPTION,0,2562,{{ time }},11.11.111.111,11.11.111.111,11.111.1.11,11.11.111.111,external-access,,,ssl,vsys1,XXX1,Internet,ethernet1/1,ethernet1/2,Log_Forwarding_Profile_XX,{{ time }},111111111,1,1111111,443,38178,443,0x400400,tcp,allow,N/A,,,,,xxxxxx-xxxxx-xxxxx-xxxx-xxxxxxx,Certificate,Certificate,TLS1.2,ECDHE,AES_128_GCM,SHA256,external-access,,None,uninspected,Uninspected,No Decrypt,xxxxx,xxxxxxxx,2025/02/10 15:21:54,2028/02/10 15:21:54,V3,2048,34,27,0,0,:::::RSA,url.com,Intermediate CA,,,,,,,,,,,{{ high_res_time }},,,,,,,,,,,,,,,,,xxx,xxx,20,0,0,0,,xx-xx-firewall-xx,1,encrypted-tunnel,networking,browser-based,4,\"used-by-malware,able-to-transfer-file,has-known-vulnerability,tunnel-other-application,pervasive-use\",,ssl,no,no\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, high_res_time=orig_timestamp_str)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="pan:decryption"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1