# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random
import pytest
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()
#486 <132>1 2022-04-05T19:56:42.387000Z Barracuda - - - src=10.1.1.1 spt=33217 dst=10.1.1.1 dpt=39971 actionTaken=DENY attackDescription=GEO_IP_BLOCK attackDetails=GeoIP Policy Match attackGroup=Forceful Browsing attackId=1111 logType=WF app=TLSv1.2 request=/apps/ requestMethod=GET rt=1649197620642 userAgent=Mozilla/5.0 [en] (X11, U; OpenVAS-VT 9.0.3) referer=
def test_barracuda(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} Barracuda - - - - src=10.1.1.1 spt=33217 dst=10.1.1.1 dpt=39971 actionTaken=DENY attackDescription=GEO_IP_BLOCK attackDetails=GeoIP Policy Match {{host }} attackGroup=Forceful Browsing attackId=1111 logType=WF app=TLSv1.2 request=/apps/ requestMethod=GET rt=1649197620642 userAgent=Mozilla/5.0 [en] (X11, U; OpenVAS-VT 9.0.3) referer='
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netwaf  host=barracuda {{ host }} sourcetype="barracuda:wf"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<134>Feb  6 14:33:07 GUI [1100:1178]: ANDR<6+info  > 1899 22514 I BetterTogether:EndpointPairingService: ProcessId: 1899, Thread: Pool-BetterTogether-Thread-462, No endpoint paired, do nothing, own endpoint: dc65acdb-b0e3-3663-b0e3-42c442c4b0e3. {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns {{ host }} sourcetype="microsoft:teams:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_2(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<134>Feb  6 14:33:10 uhes[1532.1737]: ULIU<6+info  > 390.752.699:cancel transfer 0x7638fceb98 {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns {{ host }} sourcetype="microsoft:teams:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_3(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<133>Feb  6 14:35:16 ipp [1080.1259]: IPP <5+notice> 516.689.412:ipp_event_from_dev: Message=0x00000400(0x00000001+0x00000000+0){{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns {{ host }} sourcetype="microsoft:teams:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_4(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<133>Feb  6 14:34:21 sys [1003.1015]: SYS <5+notice> old dst 0, old offset 3600, old tv sec 1675690461, new 1675690461 {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns {{ host }} sourcetype="microsoft:teams:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_5(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<133>Feb  6 14:33:31 ipvp[1073.1073]: IPVP<5+notice> 411.139.381:Message=0x00000001(0x00000000+0x00000000+0) {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns {{ host }} sourcetype="microsoft:teams:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_6(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<190>Jan 25 19:43:26 {{ host }} SFIMS: <*- Client Update From "net-sfux166a.cph.dk" at Wed Jan 25 19:43:26 2023 UTC -*>   IP Address: 10.250.32.247 Office Mobile '
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netids  host={{ host }} sourcetype="cisco:firepower:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_7(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<46>Jan 25 19:44:22 {{ host }} : HMNOTIFY: Memory Usage (Sensor net-sfux048a.cph.dk): Severity: normal: Used 4628.16MB of 11367.89MB (Physical + Swap)'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netids  host={{ host }} sourcetype="cisco:fmc:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_8(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<14>Jan 25 20:09:03 IPRep.pl: [FMC1] net-fmc1.cph.dk: csm_processes@Default User IP, Login, Login Success.x0a.x00 {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netids {{ host }} sourcetype="cisco:fmc:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_9(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<191>Jan 25 18:29:45 [CATS.PROD] SlvDB: 001-D <slv> check_for_correct_value: opr_id <5797549> , arr_dep <A> , callsign <SRN3273> , old first leg <ENAL> , new first leg <> , old transponder <> , new transponder <> {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth {{ host }} sourcetype="linux:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_10(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<175>Jan 25 18:30:12 msgmarker: D [DB::GetDetailMSG] : =====----------------------New Message---------------------------===== {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth {{ host }} sourcetype="linux:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_11(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<163>Jan 25 18:29:56 estinop-fpl02: E 402-E [CmplCommunication::CheckBulkMsg] : No connection to CMPL. Can not check BULK message from CMPL {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth {{ host }} sourcetype="linux:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_12(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<181>Feb  6 13:32:13 {{ host }} CISE_System_Statistics 0000069937 1 0 2023-02-06 13:32:13.180 +00:00 1358622814 70011 NOTICE System-Stats: ISE Counters, ConfigVersionId=87, OperationCounters=Counter=4_HostName_Event_Fetch_FromAD:0\,13_Protocol_Runtime_Context:3\,4_Probe_Requests_Dropped:0\,4_Probe_Requests_Received:0\,4_ArpCache_InsertUpdate_Received:0\,16_iowait:6\,4_EndpointCache_InsertUpdate_Received:0\,4_RadiusPacketsReceived:2199\,4_NMAP_ScanEvent_Query:0, '
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth  host={{ host }} sourcetype="cisco:ise:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_13(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<182>Feb  7 05:00:00 {{ host }} CISE_MONITORING_DATA_PURGE_AUDIT 2023-02-07 04:39:12.569 +0000 60198 INFO null: MnT purge event occurred, MESSAGE=purging Tacacs data older than 08-JAN-23,'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth  host={{ host }} sourcetype="cisco:ise:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_14(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<182>Feb  7 05:00:00 {{ host }} CISE_MONITORING_DATA_PURGE_AUDIT 2023-02-07 04:05:30.743 +0000 60198 INFO null: MnT purge event occurred, MESSAGE=Radius Data threshold_space = 250 GB, used_space = 27 GB,'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth  host={{ host }} sourcetype="cisco:ise:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_15(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '2023-02-06T14:55:00Z CEF:0|CyberArk|ApplicationMonitor|1.0.0000|MV-PAMTESTPSM01|||0|CyberArk Privileged Session Manager13.0.0.9|13.0.0.9 {{ host }}      '
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth {{ host }} sourcetype="cyberark:pms:cef"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_16(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '2023-02-06T15:00:00Z CEF:0|CyberArk|HardwareMonitor|1.0.0000|MV-PAMTESTPSM01|   0,75|55|99.4|58 {{ host }}'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth {{ host }} sourcetype="cyberark:pms:cef"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_barracuda_17(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<35>Jan 26 00:47:18  {{ host }} 10.198.4.14 sshd[25136]: TACACS+ Client: Authentication success. Server is 10.191.50.80, user name is \'snowscan\', remote address is 10.193.29.111. Authentication success.'
    )
    message = mt.render(mark="<132>1", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdns  host={{ host }} sourcetype="infoblox:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
