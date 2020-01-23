# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


#<190>Jul 27 23:31:58 VAULT CEF:0|Cyber-Ark|Vault|9.20.0000|7|Logon|5|act="Logon" suser=##USER_NAME## fname= dvc= shost=##SOURCE_IP## dhost= duser= externalId= app= reason= cs1Label="Affected User Name" cs1= cs2Label="Safe Name" cs2= cs3Label="Device Type" cs3=11111 cs4Label="Database" cs4=222222 cs5Label="Other info" cs5= cn1Label="Request Id" cn1= cn2Label="Ticket Id" cn2=  msg=
def test_cyberark_epv(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CEF:0|Cyber-Ark|Vault|9.20.0000|7|Logon|5|act=\"Logon\" suser=##USER_NAME## fname= dvc= shost=##SOURCE_IP## dhost= duser= externalId= app= reason= cs1Label=\"Affected User Name\" cs1= cs2Label=\"Safe Name\" cs2= cs3Label=\"Device Type\" cs3=11111 cs4Label=\"Database\" cs4=222222 cs5Label=\"Other info\" cs5= cn1Label=\"Request Id\" cn1= cn2Label=\"Ticket Id\" cn2=  msg=\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=netauth host=\"{{ host }}\" sourcetype=\"cyberark:epv:cef\"| head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<190>Jul 12 23:44:25 10.0.0.1 CEF:0|CyberArk|PTA|2.6.1|20|Privileged account anomaly|8|cs1Label=incidentId cs1=55a32ed8e4b0e4a90114e12c start=1436755482000 deviceCustomDate1Label=detectionDate deviceCustomDate1=1436759065017 msg=Incident updated. Now contains 7 anomalies cs2Label=link cs2=https://10.0.0.1/incidents/55a32ed8e4b0e4a90114e12c
def test_cyberark_pta(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CEF:0|CyberArk|PTA|2.6.1|20|Privileged account anomaly|8|cs1Label=incidentId cs1=55a32ed8e4b0e4a90114e12c start=1436755482000 deviceCustomDate1Label=detectionDate deviceCustomDate1=1436759065017 msg=Incident updated. Now contains 7 anomalies cs2Label=link cs2=https://10.0.0.1/incidents/55a32ed8e4b0e4a90114e12c\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cyberark:pta:cef\"| head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
