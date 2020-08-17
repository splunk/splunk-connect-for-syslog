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

testdata_cef = [
    '{{mark}} {{ bsd }} {{ host }} {{ app }}: Mon Aug 10 10:10:07 2020: CEF:0|Cisco|C100V Email Security Virtual Appliance|13.0.0-283|ESA_CONSOLIDATED_LOG_EVENT|Consolidated Log Event|5|cs6Label=SDRRepScore cs6=Weak deviceExternalId=111111111111-ZZZZZZZZZZZ ESAMID=19 startTime=Mon Aug 10 10:10:07 2020 deviceOutboundInterface=OutgoingMail ESADMARCVerdict=PermFailure dvc=1.1.1.1 ESAAttachmentDetails={\'sample_ESA_attachment\':   {\'AMP\': {\'Verdic\': \'FILE UNKNOWN\', \'fileHash\': \'35918c38cea9ad9279ad0b206091be3085874528edaf6994b73f0758679815a3\'},  \'BodyScanner\': {}}} ESAFriendlyFrom=sample_user deviceDirection=1 ESAMailFlowPolicy=ACCEPT suser=sample_user cs1Label=MailPolicy cs1=DEFAULT act=BOUNCED ESAFinalActionDetails=To SPAM cs4Label=ExternalMsgID cs4=\'<dummy@cs4>\' duser=dummy_duser ESAHeloIP=10.0.0.1 cfp1Label=SBRSScore cfp1=None ESASDRDomainAge=83 years 10 months 26 days cs3Label=SDRThreatCategory cs3=N/A ESASPFVerdict=PermError sourceHostName=unknown ESASenderGroup=SUSPECTLIST sourceAddress=5001:0db8:85a3:2222:6565:7457:0370:5453 ESAICID=30 cs5Label=ESAMsgLanguage cs5=English msg=[Cousin\=20Domain][SUSPECTED\=20SPAM]\=20asdfdsaf cs2Label=GeoLocation cs2=India ESAMsgTooBigFromSender=true ESARateLimitedIP=10.0.0.2 ESADHASource=10.0.0.3 ESAHeloDomain=test.com ESATLSOutConnStatus=Success ESATLSOutProtocol=TLSv1.2 ESATLSOutCipher=ECDHE-RSA-AES128-GCM-SHA256 ESATLSInConnStatus=Success ESATLSInProtocol=TLSv1.2 ESATLSInCipher=ECDHE-RSA-AES128-GCM-SHA256 ESADKIMVerdict=PermError ESAReplyTo=demo@test.com ESAASVerdict=SUSPECT ESAAMPVerdict=FA_PENDING ESAAVVerdict=REPAIRED ESAGMVerdict=POSITIVE ESACFVerdict=MATCH ESAOFVerdict=NEGATIVE ESADLPVerdict=NO VIOLATION ESAURLDetails={url1:{expanded_url: sample_expanded_url, category: dummy_category, wbrs_score: 62, in_attachment: sample_attachment_file, Attachment_with_url: www.sample.attachment.url.com,},url2:{…}} ESAMARAction= {action:success;succesful_rcpts=56;failed_recipients=0;filename=dummy_filename.txt} Message Filters Verdict=MATCH ESADCID=507 EndTime=Mon Aug 10 10:10:07 2020 ESADaneStatus=success ESADaneHost=testdomain.com',
];

@pytest.mark.parametrize("event", testdata_cef)
def test_cisco_esa_cef(record_property, setup_wordlist, setup_splunk, setup_sc4s, event):
    host = "cisco_esa"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, app='ESA')

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=main _time={{ epoch }} sourcetype="cisco:esa:cef" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
