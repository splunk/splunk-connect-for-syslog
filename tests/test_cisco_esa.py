# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *
import pytest

env = Environment()

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
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 09:44:51 2020 Info: logout:64.205.160.240 user:dummy_user1 session:LH09MofqDf2j21zW9QN1",
    "{{mark}} {{ bsd }} {{ host }} {{ app }}: Aug  3 07:26:33  10.0.1.1 MAR_SecurityAudit: Info: Message containing attachment(s) for which verdict update was(were) available was not found in the recipient's (<EMAIL>) mailbox.",
]


@pytest.mark.parametrize("event", testdata_http)
def test_cisco_esa_http(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_textmail)
def test_cisco_esa_textmail(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_amp)
def test_cisco_esa_amp(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_authentication)
def test_cisco_esa_authentication(
    record_property, setup_wordlist, setup_splunk, setup_sc4s, event
):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_cisco_esa_cef(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "cisco-esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
