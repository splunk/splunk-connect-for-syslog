# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment
from pytest import mark

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <190>Jan 28 01:28:35 PA-VM300-goran1 1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,1,2014/01/28 01:28:34,192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0

def test_palo_alto_traffic(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},007200C01056,TRAFFIC,end,1,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Oct 30 09:46:12 1,2012/10/30 09:46:12,01606001116,TRAFFIC,start,1,2012/04/10 04:39:58,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:59,11449,1,59324,80,0,0,0x200000,tcp,allow,78,78,0,1,2012/04/10 04:39:59,0,any,0,0,0x0,192.168.0.0-192.168.255.255,United States,0,1,0
def test_palo_alto_traffic_dvc_name(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }}-no 1,{{ time }},007200C01056,TRAFFIC,start,1,{{ time }},192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,{{ time }},11449,1,59324,80,0,0,0x200000,tcp,allow,78,78,0,1,2012/04/10 04:39:59,0,any,0,0,0x0,192.168.0.0-192.168.255.255,United States,0,1,0,unknown,dg1,dg2,dg3,dg4,vsys_n13,{{ host }},action_source,src_vm,dest_vm,tunnel_id,tunnel_monitor_tag,tunnel_session_id,tunnel_start_time,tunnel_type\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <190>Oct 30 09:46:17 1,2012/10/30 09:46:17,01606001116,THREAT,url,1,2012/04/10 04:39:55,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,"litetopdetect.cn/index.php",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html
def test_palo_alto_threat(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},01606001116,THREAT,url,1,{{ time }},192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,\"litetopdetect.cn/index.php\",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netproxy host=\"{{ host }}\" sourcetype=\"pan:threat\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <190>Jan 28 01:28:35 fooooo 1,2020/07/08 16:48:50,013201020735,THREAT,url,2049,2020/07/08 16:48:48,10.1.1.1,1.1.1.2,1.1.1.1,1.1.1.3,URLFilter_CatchAll_Internet,testuser,,arcgis,vsys1,DMZ,Outside,ae3,ae1,Panorama-Only,2020/07/08 16:48:48,357728,1,61066,80,33396,80,0x8403000,tcp,alert,"geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?distance=100&f=json&location={""x"":-33,""y"":22.3,""spatialReference"":{""wkid"":111}}",(9999),ALL-WhitelistedURLs,informational,client-to-server,6816029286804555581,0xa000000000000000,Internal,United States,0,application/json,0,,,1,,,,,,,,0,11,16,0,0,,TESTFW01,,,,get,0,,0,,N/A,unknown,AppThreat-0-0,0x0,0,4294967295,
def test_palo_alto_threat2(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},01606001116,THREAT,url,1,{{ time }},10.1.1.1,1.1.1.2,1.1.1.1,1.1.1.3,URLFilter_CatchAll_Internet,testuser,,arcgis,vsys1,DMZ,Outside,ae3,ae1,Panorama-Only,2020/07/08 16:48:48,357728,1,61066,80,33396,80,0x8403000,tcp,alert,"geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?distance=100&f=json&location={""x"":-33,""y"":22.3,""spatialReference"":{""wkid"":111}}",(9999),ALL-WhitelistedURLs,informational,client-to-server,6816029286804555581,0xa000000000000000,Internal,United States,0,application/json,0,,,1,,,,,,,,0,11,16,0,0,,{{ host }},,,,get,0,,0,,N/A,unknown,AppThreat-0-0,0x0,0,4294967295,\n')
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netproxy host=\"{{ host }}\" sourcetype=\"pan:threat\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_palo_alto_traffic_badietf(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}1 {{ bsd }} {{ host }} 1,{{ time }},007200001056,TRAFFIC,end,1,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_palo_alto_traffic_mstime(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},007200001056,TRAFFIC,end,1,{{ time }},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,{{ time }},2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


#<14>May 11 10:13:22 xxxxxx 1,2020/05/11 10:13:22,015451000001111,HIPMATCH,0,2049,2020/05/11 10:13:22,xx.xx,vsys1,xx-xxxxx-MB,Mac,10.252.31.187,GP-HIP,1,profile,0,0,1052623,0x0,17,11,12,0,,xxxxx,1,0.0.0.0,
def test_palo_alto_hipmatch(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} 1,{{ time }},015451000001111,HIPMATCH,0,2049,{{ time }},xxxx.xxx,vsys1,xx-xxxxxx-MB,Mac,10.252.31.187,GP-HIP,1,profile,0,0,1052623,0x0,17,11,12,0,,{{ host }},1,0.0.0.0,\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"pan:hipmatch\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

