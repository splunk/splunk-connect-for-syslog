# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <5>1 2020-01-24T22:53:03Z REDACTEDHOSTNAME CEF:0|Cyber-Ark|Vault|10.9.0000|22|CPM Verify Password|5|act="CPM Verify Password" suser=PasswordManager fname=Root\Operating System-OBO-ISSO-Windows-Domain-Account-redacted dvc= shost=10.0.0.10 dhost= duser=redacted externalId= app= reason= cs1Label="Affected User Name" cs1= cs2Label="Safe Name" cs2="re-dact-ted" cs3Label="Device Type" cs3="Operating System" cs4Label="Database" cs4= cs5Label="Other info" cs5= cn1Label="Request Id" cn1= cn2Label="Ticket Id" cn2="VerificationPeriod"  msg="VerificationPeriod"
@pytest.mark.addons("cyberark")
def test_cyberark_epv_5424(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}1 {{ iso }}Z {{ host }} CEF:0|Cyber-Ark|Vault|9.20.0000|7|Logon|5|act="Logon" suser=PasswordManager fname= dvc= shost=10.0.0.10 dhost= duser= externalId= app= reason= cs1Label="Affected User Name" cs1= cs2Label="Safe Name" cs2= cs3Label="Device Type" cs3=11111 cs4Label="Database" cs4=222222 cs5Label="Other info" cs5= cn1Label="Request Id" cn1= cn2Label="Ticket Id" cn2=  msg=\n'
    )
    message = mt.render(mark="<111>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cyberark:epv:cef"| head 2'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Jul 27 23:31:58 VAULT CEF:0|Cyber-Ark|Vault|9.20.0000|7|Logon|5|act="Logon" suser=user2 fname= dvc= shost=127.0.0.1 dhost= duser= externalId= app= reason= cs1Label="Affected User Name" cs1= cs2Label="Safe Name" cs2= cs3Label="Device Type" cs3=11111 cs4Label="Database" cs4=222222 cs5Label="Other info" cs5= cn1Label="Request Id" cn1= cn2Label="Ticket Id" cn2=  msg=
@pytest.mark.addons("cyberark")
def test_cyberark_epv(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} CEF:0|Cyber-Ark|Vault|9.20.0000|7|Logon|5|act="Logon" suser=user2 fname= dvc= shost=127.0.0.1 dhost= duser= externalId= app= reason= cs1Label="Affected User Name" cs1= cs2Label="Safe Name" cs2= cs3Label="Device Type" cs3=11111 cs4Label="Database" cs4=222222 cs5Label="Other info" cs5= cn1Label="Request Id" cn1= cn2Label="Ticket Id" cn2=  msg=\n'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cyberark:epv:cef"| head 2'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <190>Jul 12 23:44:25 10.0.0.1 CEF:0|CyberArk|PTA|2.6.1|20|Privileged account anomaly|8|cs1Label=incidentId cs1=55a32ed8e4b0e4a90114e12c start=1436755482000 deviceCustomDate1Label=detectionDate deviceCustomDate1=1436759065017 msg=Incident updated. Now contains 7 anomalies cs2Label=link cs2=https://10.0.0.1/incidents/55a32ed8e4b0e4a90114e12c
@pytest.mark.addons("cyberark")
def test_cyberark_pta(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{ host }} CEF:0|CyberArk|PTA|2.6.1|20|Privileged account anomaly|8|cs1Label=incidentId cs1=55a32ed8e4b0e4a90114e12c start=1436755482000 deviceCustomDate1Label=detectionDate deviceCustomDate1=1436759065017 msg=Incident updated. Now contains 7 anomalies cs2Label=link cs2=https://10.0.0.1/incidents/55a32ed8e4b0e4a90114e12c\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="cyberark:pta:cef"| head 2'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
