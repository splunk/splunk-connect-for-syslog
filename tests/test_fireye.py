# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <164>fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt=Jan 25 2021 20:37:54 UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost={{ host }} cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start=Jan 25 2021 20:37:54 UTC ","PRI":"<164>","MESSAGE":"fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt=Jan 25 2021 20:37:54 UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost={{ host }} cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start=Jan 25 2021 20:37:54 UTC
@pytest.mark.addons("fireeye")
def test_fireeye_cms(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt={{ bsd }} UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost={{ host }} cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start={{ bsd }} UTC\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=fireeye host="{{ host }}" sourcetype="fe_cef_syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# cef[24366]: CEF:0|fireeye|hx|5.0.3|FireEye Acquisition Completed|FireEye Acquisition Completed|0|rt=Jan 26 2021 02:14:17 UTC dvchost={{ host }} deviceExternalId=0CC47AA8D848 categoryDeviceGroup=/IDS/Application/Service categoryDeviceType=Forensic Investigation categoryObject=/Host cs1Label=Host Agent Cert Hash cs1=aL9HjiEIvp8d1kiwieaaHG dst=10.49.2.59 dmac=64-00-6a-54-c4-7a dhost=MZAUNG dntdom=CS deviceCustomDate1Label=Agent Last Audit deviceCustomDate1=Jan 26 2021 02:13:19 UTC cs2Label=FireEye Agent Version cs2=32.30.0 cs5Label=Target GMT Offset cs5=+PT6H30M cs6Label=Target OS cs6=Windows 10 Enterprise 15063 externalId=1003 cs3Label=Script Name cs3=Bulk Acquisition suser=fe_services act=Acquisition Status in=1361 categoryOutcome=/Success categorySignificance=/Informational categoryBehavior=/Access/Start msg=Host MZAUNG Bulk Acquisition completed categoryTupleDescription=A Host Acquisition was successfully completed.
@pytest.mark.addons("fireeye")
def test_fireeye_hx(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}cef[24366]: CEF:0|fireeye|hx|5.0.3|FireEye Acquisition Completed|FireEye Acquisition Completed|0|rt={{ bsd }} UTC dvchost={{ host }} deviceExternalId=0CC47AA8D848 categoryDeviceGroup=/IDS/Application/Service categoryDeviceType=Forensic Investigation categoryObject=/Host cs1Label=Host Agent Cert Hash cs1=aL9HjiEIvp8d1kiwieaaHG dst=10.49.2.59 dmac=64-00-6a-54-c4-7a dhost=MZAUNG dntdom=CS deviceCustomDate1Label=Agent Last Audit deviceCustomDate1=Jan 26 2021 02:13:19 UTC cs2Label=FireEye Agent Version cs2=32.30.0 cs5Label=Target GMT Offset cs5=+PT6H30M cs6Label=Target OS cs6=Windows 10 Enterprise 15063 externalId=1003 cs3Label=Script Name cs3=Bulk Acquisition suser=fe_services act=Acquisition Status in=1361 categoryOutcome=/Success categorySignificance=/Informational categoryBehavior=/Access/Start msg=Host MZAUNG Bulk Acquisition completed categoryTupleDescription=A Host Acquisition was successfully completed.\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=fireeye host="{{ host }}" sourcetype="hx_cef_syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# 2021-03-03T20:14:22.226Z CEF:0|FireEye|ETP|3.0|etp|malicious email|10|rt=Mar 03 2021:20:07:54 UTC suser=redacted@redacted.com duser=redacted@redacted.com fname=hxxps://redacted[dot]com/foo fileHash=123456789abcdef destinationDnsDomain=redacted.com externalId=123456789 cs1Label=sname cs1=Phish.LIVE.DTI.URL cs3Label=Subject cs3=Subject Redacted cs4Label=Link cs4=https://etp.us.fireeye.com/alert/123456789/ cs5Label=Client cs5=REDACTED-COMPANY
@pytest.mark.addons("fireeye")
def test_fireeye_etp(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ iso }} CEF:0|FireEye|ETP|3.0|etp|malicious email|10|rt={{ bsd }} UTC suser=redacted@redacted.com duser=redacted@redacted.com fname=hxxps://redacted[dot]com/foo fileHash=123456789abcdef destinationDnsDomain=redacted.com externalId=123456789 cs1Label=sname cs1=Phish.LIVE.DTI.URL cs3Label=Subject cs3=Subject Redacted cs4Label=Link cs4=https://etp.us.fireeye.com/alert/123456789/ cs5Label=Client cs5={{ host }} \n"
    )
    message = mt.render(mark="<111>", iso=iso, bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=fireeye "{{ host }}" sourcetype="fe_etp"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fireeye")
def test_fireeye_hx_json_1(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<164>fenotify-7441437.warning: {"msg":"normal","appliance-id":"xxxxx","product":"HX","appliance":"AAAAA-D-PR-FIREEYEHX01-ISD-MTE.xxxxx","version":"5.0.0.0000","alert":{"host":{"gmt_offset_seconds":39600,"agent_version":"32.30.0","hostname":"{{ host }}","os":"Windows 10 Enterprise","ip":"10.42.100.7","agent_id":"xxxxxx","containment_state":"normal","domain":"CORPTESTAU"},"matched_at":"2021-02-25T06:02:37+00:00","condition":{"_id":"111111","tests":[{"operator":"contains","token":"processEvent/processCmdLine","value":"cmd","type":"text"},{"operator":"equal","token":"processEvent/process","value":"psexec.exe","type":"text"},{"operator":"matches","token":"processEvent/processCmdLine","value":"\\\\\\\\\\\\\\\\","type":"text"}],"enabled":true},"resolution":"ALERT","_id":7536719,"reported_at":"2021-02-25T06:02:54.035+00:00","sysinfo":{"_id":"xxxxxx","mac_address":"xxxxxx"},"indicator":{"display_name":"T1035-SERVICE-EXEC_PsExec","_id":"xxxxxx","uri_name":"xxxxxx","description":"Adversaries may execute a binary, command, or script via a method that interacts with Windows services, such as the Service Control Manager. This can be done by either creating a new service or modifying an existing service. This technique is the execution used in conjunction with New Service and Modify Existing Service during service persistence or privilege escalation.\\n\\nPsExec allows redirects of the input and output of a remotely started executable through the use of SMB and the hidden $ADMIN share on the remote system. With this share, PsExec uses the Windows Service control Manager API to start the PsExecsvc service on the remote system which creates a named pipe that PsExec communicates with. This named pipe is what allows for input/output redirection back to the system that launched PsExec.","category_id":2,"signature":null},"indicator_category":{"_id":2,"uri_name":"Custom"},"event_id":111111,"event_at":"2021-02-25T06:02:28.113+00:00","source":"IOC","event_type":"processEvent","matched_source_alerts":null,"event_values":{"processEvent/startTime":"2021-02-25T06:02:28.113Z","processEvent/timestamp":"{{ iso }}","processEvent/parentProcess":"cmd.exe","processEvent/eventType":"start","processEvent/parentPid":7880,"processEvent/processPath":"C:\\\\build\\\\PSTools\\\\PsExec.exe","processEvent/pid":12320,"processEvent/process":"PsExec.exe","processEvent/parentProcessPath":"C:\\\\Windows\\\\System32\\\\cmd.exe","processEvent/md5":"111111","processEvent/username":"CORPTESTAU\\\\xxxxxxx","processEvent/processCmdLine":"psexec  \\\\\\\\auae0501vt1038 cmd"},"uuid":"b36909ea-948f-44db-8319-76526cb64b40","name":"indicator-executed"}}\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=fireeye host="{{ host }}" sourcetype="hx_json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fireeye")
def test_fireeye_hx_json_2(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<164>fenotify-7441437.warning: {"msg":"normal","appliance-id":"xxxxx","product":"HX","appliance":"AAAAA-D-PR-FIREEYEHX01-ISD-MTE.xxxxx","version":"5.0.0.0000","alert":{"host":{"gmt_offset_seconds":39600,"agent_version":"32.30.0","hostname":"{{ host }}","os":"Windows 10 Enterprise","ip":"10.42.100.7","agent_id":"xxxxxx","containment_state":"normal","domain":"CORPTESTAU"},"matched_at":"2021-02-25T06:02:37+00:00","condition":{"_id":"111111","tests":[{"operator":"contains","token":"processEvent/processCmdLine","value":"cmd","type":"text"},{"operator":"equal","token":"processEvent/process","value":"psexec.exe","type":"text"},{"operator":"matches","token":"processEvent/processCmdLine","value":"\\\\\\\\\\\\\\\\","type":"text"}],"enabled":true},"resolution":"ALERT","_id":7536719,"reported_at":"2021-02-25T06:02:54.035+00:00","sysinfo":{"_id":"xxxxxx","mac_address":"xxxxxx"},"indicator":{"display_name":"T1035-SERVICE-EXEC_PsExec","_id":"xxxxxx","uri_name":"xxxxxx","description":"Adversaries may execute a binary, command, or script via a method that interacts with Windows services, such as the Service Control Manager. This can be done by either creating a new service or modifying an existing service. This technique is the execution used in conjunction with New Service and Modify Existing Service during service persistence or privilege escalation.\\n\\nPsExec allows redirects of the input and output of a remotely started executable through the use of SMB and the hidden $ADMIN share on the remote system. With this share, PsExec uses the Windows Service control Manager API to start the PsExecsvc service on the remote system which creates a named pipe that PsExec communicates with. This named pipe is what allows for input/output redirection back to the system that launched PsExec.","category_id":2,"signature":null},"indicator_category":{"_id":2,"uri_name":"Custom"},"event_id":111111,"event_at":"2021-02-25T06:02:28.113+00:00","source":"IOC","event_type":"processEvent","matched_source_alerts":null,"event_values":{"processEvent/startTime":"2021-02-25T06:02:28.113Z","processEvent/parentProcess":"cmd.exe","processEvent/eventType":"start","processEvent/parentPid":7880,"processEvent/processPath":"C:\\\\build\\\\PSTools\\\\PsExec.exe","processEvent/pid":12320,"processEvent/process":"PsExec.exe","processEvent/parentProcessPath":"C:\\\\Windows\\\\System32\\\\cmd.exe","processEvent/md5":"111111","processEvent/username":"CORPTESTAU\\\\xxxxxxx","processEvent/processCmdLine":"psexec  \\\\\\\\auae0501vt1038 cmd"},"uuid":"b36909ea-948f-44db-8319-76526cb64b40","name":"indicator-executed"}}\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=fireeye host="{{ host }}" sourcetype="hx_json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fireeye")
def test_fireeye_hx_json_with_hdr(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        '<164>2021-07-26T09:47:48.965+00:00 10.00.000.00 fenotify-7441437.warning: {"msg":"normal","appliance-id":"xxxxx","product":"HX","appliance":"AAAAA-D-PR-FIREEYEHX01-ISD-MTE.xxxxx","version":"5.0.0.0000","alert":{"host":{"gmt_offset_seconds":39600,"agent_version":"32.30.0","hostname":"{{ host }}","os":"Windows 10 Enterprise","ip":"10.42.100.7","agent_id":"xxxxxx","containment_state":"normal","domain":"CORPTESTAU"},"matched_at":"2021-02-25T06:02:37+00:00","condition":{"_id":"111111","tests":[{"operator":"contains","token":"processEvent/processCmdLine","value":"cmd","type":"text"},{"operator":"equal","token":"processEvent/process","value":"psexec.exe","type":"text"},{"operator":"matches","token":"processEvent/processCmdLine","value":"\\\\\\\\\\\\\\\\","type":"text"}],"enabled":true},"resolution":"ALERT","_id":7536719,"reported_at":"2021-02-25T06:02:54.035+00:00","sysinfo":{"_id":"xxxxxx","mac_address":"xxxxxx"},"indicator":{"display_name":"T1035-SERVICE-EXEC_PsExec","_id":"xxxxxx","uri_name":"xxxxxx","description":"Adversaries may execute a binary, command, or script via a method that interacts with Windows services, such as the Service Control Manager. This can be done by either creating a new service or modifying an existing service. This technique is the execution used in conjunction with New Service and Modify Existing Service during service persistence or privilege escalation.\\n\\nPsExec allows redirects of the input and output of a remotely started executable through the use of SMB and the hidden $ADMIN share on the remote system. With this share, PsExec uses the Windows Service control Manager API to start the PsExecsvc service on the remote system which creates a named pipe that PsExec communicates with. This named pipe is what allows for input/output redirection back to the system that launched PsExec.","category_id":2,"signature":null},"indicator_category":{"_id":2,"uri_name":"Custom"},"event_id":111111,"event_at":"2021-02-25T06:02:28.113+00:00","source":"IOC","event_type":"processEvent","matched_source_alerts":null,"event_values":{"processEvent/startTime":"2021-02-25T06:02:28.113Z","processEvent/timestamp":"{{ iso }}","processEvent/parentProcess":"cmd.exe","processEvent/eventType":"start","processEvent/parentPid":7880,"processEvent/processPath":"C:\\\\build\\\\PSTools\\\\PsExec.exe","processEvent/pid":12320,"processEvent/process":"PsExec.exe","processEvent/parentProcessPath":"C:\\\\Windows\\\\System32\\\\cmd.exe","processEvent/md5":"111111","processEvent/username":"CORPTESTAU\\\\xxxxxxx","processEvent/processCmdLine":"psexec  \\\\\\\\auae0501vt1038 cmd"},"uuid":"b36909ea-948f-44db-8319-76526cb64b40","name":"indicator-executed"}}\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=fireeye host="{{ host }}" sourcetype="hx_json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
