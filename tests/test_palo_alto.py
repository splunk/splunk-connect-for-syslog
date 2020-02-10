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

env = Environment(extensions=['jinja2_time.TimeExtension'])

#<190>Jan 28 01:28:35 PA-VM300-goran1 1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,1,2014/01/28 01:28:34,192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0
def test_palo_alto_traffic(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},007200001056,TRAFFIC,end,1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <190>Oct 30 09:46:17 1,2012/10/30 09:46:17,01606001116,THREAT,url,1,2012/04/10 04:39:55,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,"litetopdetect.cn/index.php",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html
def test_palo_alto_threat(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},01606001116,THREAT,url,1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,\"litetopdetect.cn/index.php\",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netproxy host=\"{{ host }}\" sourcetype=\"pan:threat\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_palo_alto_traffic_badietf(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}1 {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},007200001056,TRAFFIC,end,1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@mark.skip()
def test_palo_alto_traffic_mstime(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S.%f' %},007200001056,TRAFFIC,end,1,{% now 'utc', '%Y/%m/%d %H:%M:%S.%f' %},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,{% now 'utc', '%Y/%m/%d %H:%M:%S.%f' %},2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"pan:traffic\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
