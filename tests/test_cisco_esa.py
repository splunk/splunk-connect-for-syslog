# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

testdata_http = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Thu Aug 07 11:57:16 2020 Info: http service on 195.166.21.135:16872 redirecting to https port 16872",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:08:00 2020 Info: Session LH09MofqDf2j21zW9QN4 from 157.38.13.214 not found",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:10:30 2020 Info: PERIODIC REPORTS: PERIODIC_REPORTS.SYSTEM.STARTED",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:40:17 2020 Info: req:40.40.13.164 user:dummy_user1 id:LH09MofqDf2j21zW9QN2 200 GET /css/xyz HTTP/1.1 Mozilla/5.0 (Linux; U; Android 2.2.3; en-us; Droid Build/FRK76) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:12:39 2020 7.37.118.246 testmaillog: Info: Version: 8.7.2-004 SN: 942B2B684C96-29WTPQ2",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:25:08 2020 Info: System is coming up.",
]

testdata_textmail = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Jul 16 10:46:46 2013 dummy_source_Domain2 mail_logs: Info: Version: 8.7.2-001 SN: 942B2B684C96-29WTPQ2",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:00:24 2020 Info: MID 192034 not completely scanned by SDS. Error: The number of URLs in the message attachments exceeded the URL scan limit.",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:52:59 2020 Info: ICID 442736 ACCEPT SG UNKNOWNLIST match sbrs[-2.0:10.0] SBRS -0.9",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:58:54 2020 Info: DCID 112095 TLS success protocol TLSv1 cipher AES128-SHA for dummy_domain.com",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:56:56 2020 Info: Message 548799 to RID [712290] pending till Mon Aug 10 09:56:56 2020",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Aug  2 23:59:52 10.0.1.1 MAIL_SecurityAudit: Info: MID 308049623 using engine: SPF Verdict Cache using cached verdict",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Jul 26 23:48:23 10.0.1.1 CES_VPN_Mail_SecurityAudit: Info: ICID 67542 Delayed HAT REJECT continuing session for recipient logging (223.71.167.166)",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Jul 23 12:23:59 SplunkMailSyslog: Info: SenderBase upload: 734 hosts totaling 201887 bytes",
]

testdata_amp = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:04:39 2020 Info:  File uploaded for analysis. SHA256: 0172405634de890c729397377d975f059ef0becc3d072e8181d875a58eab1861, file name: Agenda_March15v3.doc",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:38:44 2020 Info:  File not uploaded for analysis.  MID = 357876 File SHA256[d7e25b63dcfe76d5528188fc801b847b4a98d6ad7234a3b2d93725d94b010e77] file mime[application/pdf] Reason: Analysis request is takenup",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:41:02 2020 Info:  Response received for file reputation query from Cloud. File Name = 'tqps.rtf', MID = 166267, Disposition = MALICIOUS, Malware = W32.C78352D892-95.SBX.TG,  Reputation Score = 1, sha256 = 756a0c3fc7d82abb243795751174053f106b7b54e431778068fa7920064268e0, upload_action = 1",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:45:53 2020 Info:  File reputation query initiating. File Name = 'Nursing Management Agenda.pdf', MID = 852867, File Size = 189 bytes, File Type = application/pdf",
]

testdata_authentication = [
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:11:29 2020 Info: Begin Logfile",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:51:36 2020 Info: User dummy_user from 125.65.72.214 was authenticated successfully.",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:01:26 2020 Info: The user admin successfully logged on from 74.151.97.24 using an HTTPS connection.",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:21:59 2020 Info: An authentication attempt by the user dummy_user1 from 27.148.207.85 failed",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:44:11 2020 Info: Time offset from UTC: 19207 seconds",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:43:53 2020 Info: User dummy_user2 from 184.186.3.161 failed authentication.",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:37:45 2020 Info: Version: 8.7.2-004 SN: 1024E857D276-JXKWBK2",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:44:51 2020 Info: login:2.85.228.227 user:dummy_user2 session:LH09MofqDf2j21zW9QN5",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:44:51 2020 Info: logout:64.205.160.240 user:dummy_user1 session:LH09MofqDf2j21zW9QN1",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:44:51 2020 Info: PID 2585: User admin logged out from session because of inactivity timeout.",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Aug  3 07:26:33  10.0.1.1 MAR_SecurityAudit: Info: Message containing attachment(s) for which verdict update was(were) available was not found in the recipient's (<EMAIL>) mailbox.",
]

testdata_gui_logs = [
    "{{mark}} {{ bsd }} {{ app }}: Info: req:45.155.204.227 user:- id:J0P3PoXjHfoHEne26uN9 200 GET /login HTTP/1.1 python-requests/2.26.0",
    "{{mark}} {{ bsd }} {{ app }}: Critical: Error in http connection from host 186.4.125.48 port 33275 - not indexable",
    "{{mark}} {{ bsd }} {{ app }}: Warning: SSL error with client 209.141.51.176:37222 - (336027804, 'error:1407609C:SSL routines:SSL23_GET_CLIENT_HELLO:http request')",
]

testdata_mail_logs = [
    "{{mark}} {{ bsd }} {{ app }}: Warning: Internal SMTP Error: Failed to send message to host 68.232.146.108:25 for recipient abc@gmail.com: Unexpected SMTP response 553, expecting code starting with 2, response was ['#5.1.8 Domain of sender address <alert@cisco.esa> does not exist'].",
    "{{mark}} {{ bsd }} {{ app }}: Info: Internal SMTP system successfully sent a message to alerts@ironport.com with subject 'AutoSupport from Cisco IronPort C000V, cisco.esa'.",
    "{{mark}} {{ bsd }} {{ app }}: Info: A System/Info alert was sent to alerts@ironport.com with subject AutoSupport from Cisco IronPort C000V, cisco.esa.",
]

testdata_amp_logs = [
    "{{mark}} {{ bsd }} {{ app }}: Info: Version: 14.0.0-698 SN: 421F6D8FB9C75E19C425-C9AEA81B2B70",
]

testdata_antispam = [
    "{{mark}} {{ bsd }} {{ app }}: Info: case antispam - engine (20078) : case-daemon: server started on UNIX domain socket [tmpdir]case_srv.sock (running version 3.10.0)",
    "{{mark}} {{ bsd }} {{ app }}: Info: case antispam - engine (20078) : case-daemon: server pid: 20078",
    "{{mark}} {{ bsd }} {{ app }}: Info: case antispam - engine (20477) : case-daemon: Initializing Child",
]

testdata_content_scanner = [
    "{{mark}} {{ bsd }} {{ app }}: Info: PF: Starting multi-threaded Perceptive server (pid=92062)",
    "{{mark}} {{ bsd }} {{ app }}: Info: PF: Restarting content_scanner service.",
]

testdata_error_logs = [
    "{{mark}} {{ bsd }} {{ app }}: Critical: Internal SMTP giving up on message to abc@splunk.com with subject 'AutoSupport from Cisco IronPort C000V, cisco.esa': Unrecoverable error.",
    "{{mark}} {{ bsd }} {{ app }}: Critical: Error while sending alert: Unable to send System/Info alert to dhruvp@splunk.com with subject AutoSupport from Cisco IronPort C000V, cisco.esa.",
]

testdata_system_logs = [
    "{{mark}} {{ bsd }} {{ app }}: Warning: Received an invalid DNS Response: '' to IP 104.244.72.10 looking up smtprdns3.werschreitdersiegt.de",
    "{{mark}} {{ bsd }} {{ app }}: Info: lame DNS referral: qname:173-212-12-198.cpe.surry.net ns_name:dns1.surry.net zone:cpe.surry.net ref_zone:cpe.surry.net referrals:[(524666183436709L, 0, 'insecure', 'dns1.surry.net'), (524666183436709L, 0, 'insecure', 'dns2.surry.net')]",
]

testdata_antivirus = [
    """{{mark}} {{ bsd }} {{ host }} {{ app }}: Warning: sophos antivirus - The Anti-Virus database on this system is expired. Although the system
will continue to scan for existing viruses, new virus updates will no
longer be available. Please run avupdate to update to the latest engine
immediately. Contact Cisco IronPort Customer Support if you have any
questions.

Current Sophos Anti-Virus Information:

SAV Engine Version 5.88
IDE Serial Unknown
Last Engine Update Sat Apr 13 15:35:20 2024
Last IDE Update Sat Apr 13 15:35:20 2024
""" ]

testdata_euq_logs =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: ISQ: out of limit action changed to 'DELETE OLDEST'"
]

testdata_service_logs =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: service_log_client.telemetry_rpc_server : THR: Thread-152: ESA messages results sent for the MID: 107."
]

testdata_reportd_logs =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: TLS connection failed because of an unsupported protocol issue. Alert message is sent in plain text to user1@esa.com"
]

testdata_sntpd_logs =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: The system time was changed from Sun, 16 Jun 2024 21:00:52 to Sun, 16 Jun 2024 21:00:53 using information from 207.54.66.52."
]

testdata_smartlicense =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: Hostname is successfully changed to ironport.esa.com for the product."
]

testdata_updater_logs =[
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Info: case waiting for new updates"
]

@pytest.mark.parametrize("event", testdata_gui_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_gui_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="gui_logs")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:http" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_mail_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_mail_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="mail_logs")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:textmail" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_antispam)
@pytest.mark.addons("cisco")
def test_cisco_esa_antispam(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="antispam")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:antispam" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_content_scanner)
@pytest.mark.addons("cisco")
def test_cisco_esa_content_scanner(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="content_scanner")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:content_scanner" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_error_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_error_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="error_logs")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:error_logs" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_antivirus)
@pytest.mark.addons("cisco")
def test_cisco_esa_antivirus(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="antivirus",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:antivirus" source=esa:antivirus _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_euq_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_euq_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="euq_logs",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:system_logs" source=esa:euq_logs _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_service_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_service_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="service_logs",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:system_logs" source=esa:service_logs _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_reportd_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_reportd_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="reportd_logs",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:system_logs" source=esa:reportd_logs _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_sntpd_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_sntpd_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="sntpd_logs",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:system_logs" source=esa:sntpd_logs _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_smartlicense)
@pytest.mark.addons("cisco")
def test_cisco_esa_smartlicense(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="smartlicense",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:system_logs" source=esa:smartlicense _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_updater_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_updater_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="updater_logs",host="ironport.esa.com")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:error_logs" source=esa:updater_logs _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_antispam)
@pytest.mark.addons("cisco")
def test_cisco_esa_antispam(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="antispam")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:antispam" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_amp_logs)
@pytest.mark.addons("cisco")
def test_cisco_esa_amp_logs(
    record_property,  setup_splunk, setup_sc4s, event
):

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, app="amp")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9000])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:amp" _raw="{{ message }}"'
    )
    message1 = mt.render(mark="", bsd="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_http)
@pytest.mark.addons("cisco")
def test_cisco_esa_http(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:http" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_textmail)
@pytest.mark.addons("cisco")
def test_cisco_esa_textmail(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:textmail" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_amp)
@pytest.mark.addons("cisco")
def test_cisco_esa_amp(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:amp" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", testdata_authentication)
@pytest.mark.addons("cisco")
def test_cisco_esa_authentication(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=email _time={{ epoch }} sourcetype="cisco:esa:authentication" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1[2:])

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_esa_cef1(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }}: CEF:0|Cisco|C100V Email Security Virtual Appliance|13.0.0-283|ESA_CONSOLIDATED_LOG_EVENT|Consolidated Log Event|5| cs6Label={{ host }} cs6=Weak deviceExternalId=111111111111-ZZZZZZZZZZZ ESAMID=81 startTime=Mon Aug 10 09:26:47 2020 deviceInboundInterface=Incoming ESADMARCVerdict=Skipped dvc=1.1.1.1 ESAAttachmentDetails={'sample_ESA_attachment':   {'AMP': {'Verdict': 'FILE UNKNOWN', 'fileHash': 'c4b06a7c1886e6785b19a5e59d595b3e6fb38be4903b55b06087948db2a4dc8b'},  'BodyScanner': {}}} ESAFriendlyFrom=sample_user deviceDirection=0 ESAMailFlowPolicy=ACCEPT suser=sample_user cs1Label=MailPolicy cs1=DEFAULT act=DQ ESAFinalActionDetails=To POLICY cs4Label=ExternalMsgID cs4='<dummy@cs4>' duser=sample_duser ESAHeloIP=10.0.0.1 cfp1Label=SBRSScore cfp1=None ESASDRDomainAge=50 years 10 months 17 days cs3Label=SDRThreatCategory cs3=N/A ESASPFVerdict=None sourceHostName=unknown ESASenderGroup=UNKNOWNLIST sourceAddress=192.11.36.3 ESAICID=91 cs5Label=ESAMsgLanguage cs5=English msg=This is a sample subject cs2Label=GeoLocation cs2=India ESAMsgTooBigFromSender=true ESARateLimitedIP=10.0.0.2 ESADHASource=10.0.0.3 ESAHeloDomain=test.com ESATLSOutConnStatus=Success ESATLSOutProtocol=TLSv1.2 ESATLSOutCipher=ECDHE-RSA-AES128-GCM-SHA256 ESATLSInConnStatus=Success ESATLSInProtocol=TLSv1.2 ESATLSInCipher=ECDHE-RSA-AES128-GCM-SHA256 ESADKIMVerdict=None ESAReplyTo=demo@test.com ESAASVerdict=SOCIAL_MAIL ESAAMPVerdict=UNSCANNABLE ESAAVVerdict=UNSCANNABLE ESAGMVerdict=POSITIVE ESACFVerdict=MATCH ESAOFVerdict=POSITIVE ESADLPVerdict=VIOLATION ESAURLDetails={url1:{expanded_url: sample_expanded_url, category: sample_category, wbrs_score: 45, in_attachment: dummy_attachment_file, Attachment_with_url: www.sample.attachment.url.com,},url2:{…}} ESAMARAction= {action:failure;succesful_rcpts=0;failed_recipients=41;filename=dummy_filename.txt} Message Filters Verdict=NO MATCH ESADCID=857 EndTime=Mon Aug 10 09:26:47 2020 ESADaneStatus=failure ESADaneHost=testdomain.com"
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email "{{ host }}" sourcetype="cisco:esa:cef" source="esa:consolidated"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_esa_cef2(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }}: CEF:0|Cisco|C300V Secure Email Gateway Virtual|14.2.0-620|ESA_CONSOLIDATED_LOG_EVENT|Consolidated Log Event|5|deviceExternalId={{ host }} ESAMID=9999999 ESAICID=22222 ESADCID=3333333 ESAAMPVerdict=NOT_EVALUATED ESAASVerdict=NOT_EVALUATED ESAAVVerdict=NOT_EVALUATED ESACFVerdict=NO_MATCH endTime=Fri Oct 21 11:10:02 2022 ESADLPVerdict=NOT_EVALUATED dvc=172.26.0.0 ESAFriendlyFrom=mail@mail.com ESAGMVerdict=NOT_EVALUATED startTime=Fri Oct 21 11:10:02 2022 deviceOutboundInterface=OutgoingMail deviceDirection=1 ESAMailFlowPolicy=RELAY suser=mail@mail.com cs1Label=MailPolicy cs1=DEFAULT cs2Label=SenderCountry cs2=not enabled ESAMFVerdict=NOT_EVALUATED act=DELIVERED cs4Label=ExternalMsgID cs4='635261e9.lFiApPMHkzd55Vmz%mail@mail.com' ESAOFVerdict=NOT_EVALUATED duser=mail@mail.com ESAHeloDomain=machine.domain.net ESAHeloIP=10.0.0.0 cfp1Label=SBRSScore cfp1=not enabled sourceHostName=unknown ESASenderGroup=RELAYLIST sourceAddress=10.0.0.0 msg='MSG' ESATLSOutCipher=ECDHE-RSA-AES256-GCM-SHA384 ESATLSOutConnStatus=Success ESATLSOutProtocol=TLSv1.2"
        + "\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, app="ESA")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email "{{ host }}" sourcetype="cisco:esa:cef" source="esa:consolidated"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
