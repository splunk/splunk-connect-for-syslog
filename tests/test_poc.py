#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause
import random
import socket
import urllib.request
from time import sleep

import pytest
from flaky import flaky
import splunklib.client as client
from jinja2 import Environment

env = Environment(extensions=['jinja2_time.TimeExtension'])


@pytest.fixture
def setup_wordlist():
    word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
    response = urllib.request.urlopen(word_url)
    long_txt = response.read().decode()
    return long_txt.splitlines()


@pytest.fixture
def setup_splunk():
    tried = 0
    while True:
        try:
            c = client.connect(username="admin", password="Changed@11", host="splunk", port="8089")
            break
        except ConnectionRefusedError:
            tried += 1
            if tried > 180:
                raise
            sleep(1)
    return c


def sendsingle(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('sc4s', 514)

    tried = 0
    while True:
        try:
            sock.connect(server_address)
            break
        except socket:
            tried += 1
            if tried > 90:
                raise
            sleep(1)
    sock.sendall(str.encode(message))
    sock.close()


def splunk_single(service, search):
    kwargs_normalsearch = {"exec_mode": "normal"}
    tried = 0
    while True:
        job = service.jobs.create(search, **kwargs_normalsearch)

        # A normal search returns the job's SID right away, so we need to poll for completion
        while True:
            while not job.is_ready():
                pass
            stats = {"isDone": job["isDone"],
                     "doneProgress": float(job["doneProgress"]) * 100,
                     "scanCount": int(job["scanCount"]),
                     "eventCount": int(job["eventCount"]),
                     "resultCount": int(job["resultCount"])}

            if stats["isDone"] == "1":
                break
            sleep(2)

        # Get the results and display them
        resultCount = stats["resultCount"]
        eventCount = stats["eventCount"]
        if resultCount > 0 or tried > 15:
            break
        else:
            tried += 1
            sleep(1)
    return resultCount, eventCount


@flaky(max_runs=3, min_passes=2)
def test_defaultroute(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %}.000z {{ host }} sc4s_default[0]: test\n")
    message = mt.render(mark="<111>1", host=host)

    sendsingle(message)

    st = env.from_string("search index=main \"{{ host }}\" sourcetype=\"syslog:fallback\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<190>Jan 28 01:28:35 PA-VM300-goran1 1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,1,2014/01/28 01:28:34,192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0
@flaky(max_runs=3, min_passes=2)
def test_palo_alto_traffic(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},007200001056,TRAFFIC,end,1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"pan:traffic\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<190>Oct 30 09:46:17 1,2012/10/30 09:46:17,01606001116,THREAT,url,1,2012/04/10 04:39:55,192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,"litetopdetect.cn/index.php",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html
@flaky(max_runs=3, min_passes=2)
def test_palo_alto_threat(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} 1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},01606001116,THREAT,url,1,{% now 'utc', '%Y/%m/%d %H:%M:%S' %},192.168.0.2,204.232.231.46,0.0.0.0,0.0.0.0,rule1,crusher,,web-browsing,vsys1,trust,untrust,ethernet1/2,ethernet1/1,forwardAll,2012/04/10 04:39:57,22860,1,59303,80,0,0,0x208000,tcp,alert,\"litetopdetect.cn/index.php\",(9999),not-resolved,informational,client-to-server,0,0x0,192.168.0.0-192.168.255.255,United States,0,text/html\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"pan:threat\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#Apr 15 2017 00:21:14 192.168.12.1 : %ASA-5-111010: User 'john', running 'CLI' from IP 0.0.0.0, executed 'dir disk0:/dap.xml'
#Apr 15 2017 00:22:27 192.168.12.1 : %ASA-4-313005: No matching connection for ICMP error message: icmp src outside:81.24.28.226 dst inside:72.142.17.10 (type 3, code 0) on outside interface. Original IP payload: udp src 72.142.17.10/40998 dst 194.153.237.66/53.
#Apr 15 2017 00:22:42 192.168.12.1 : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
@flaky(max_runs=3, min_passes=2)
def test_cisco_asa_tradditional(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:asa\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<166>2018-06-27T12:17:46Z asa : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
def test_cisco_asa_rfc5424(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%SZ' %} {{ host }} : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/5424 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<166>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:asa\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

