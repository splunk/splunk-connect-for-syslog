# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random
import uuid

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <141>Oct 24 21:05:43 smg-1 conduit: [Brightmail] (NOTICE:7500.3119331456): [12066] 'BrightSig3 Newsletter Rules' were updated successfully.
def test_symantec_brightmail(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} conduit: [Brightmail] (NOTICE:7500.3119331456): [12066] 'BrightSig3 Newsletter Rules' were updated successfully.")
    message = mt.render(mark="<134>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=email host=\"{{ host }}\" sourcetype=\"symantec:smg\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_symantec_brightmail_msg(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    msgid = uuid.uuid4()

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("""{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|VERDICT|someone@example.com|none|default|default\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|FIRED|someone@example.com|none\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|UNTESTED|someone@example.com|safe|opl|content_1574820902092|content_1574820956288|content_1574821059194|content_1574821017042|sys_deny_ip|sys_allow_ip|sys_deny_email|dns_allow|dns_deny|user_allow|user_deny|freq_va|freq_dha|freq_sa|connection_class_0|connection_class_1|connection_class_2|connection_class_3|connection_class_4|connection_class_5|connection_class_6|connection_class_7|connection_class_8|connection_class_9|blockedlang|knownlang\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|LOGICAL_IP|200.200.200.154\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|google-play_111-33.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|mac_appstore_136_33.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|6f0c8ad8-e0da-4bcc-aac9-8fa71ba43bb6.jpg\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|b340ec99-9c66-4a19-a2f4-ee467e0d63e1.jpg\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|product-logo.update.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|header-research.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195989|{{ MSGID }}|ATTACHFILTER|ms-logo-138.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|ATTACH|ms-logo-138.png|header-research.png|product-logo.update.png|b340ec99-9c66-4a19-a2f4-ee467e0d63e1.jpg|6f0c8ad8-e0da-4bcc-aac9-8fa71ba43bb6.jpg|mac_appstore_136_33.png|google-play_111-33.png\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|EHLO|mail6.bemta23.messagelabs.com\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|MSG_SIZE|94239\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|MSGID| <7jszytr60wmja@example.com>\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|SUBJECT|pulse: this is a subject\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195988|{{ MSGID }}|SOURCE|external\n
{{ mark }}{{ bsd }} {{host}} bmserver: 1576195987|{{ MSGID }}|VERDICT|<none>|connection_class_1|default|static connection class 1\n""")
    message = mt.render(mark="<1>", bsd=bsd, host=host, MSGID=msgid)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=email host=\"{{ host }}\" sourcetype=\"symantec:smg:mail\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
