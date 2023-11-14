# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


testdata = [
    '{{ mark }}{{ bsd }} {{ host }} StealthINTERCEPT - Authentication Auth failed - PolicyName="AD: Unsuccessful Account Authentications" Domain="TST" Server="TST\jsmith" ServerAddress="10.233.203.51" Perpetrator="TST\jsmith" ClientHost="SB9PCDC01.TST.TSTUSA.CORP" ClientAddress="10.230.200.11" TargetHost="SB9PCDC01.XX.XXXX.CORP" TargetHostIP="10.230.200.11" ModifiedObject="TST\\xxx" DistinguishedName="CN=Smith\, xxx,OU=User,OU=Windows 7,DC=TST,DC=XXX,DC=CORP" ObjectClass="user" SuccessfulChange="False" BlockedEvent="False" AttributeName="" Operation="" NewAttributeValue="" OldAttributeValue=""',
]


@pytest.mark.addons("stealthwatch")
@pytest.mark.parametrize("event", testdata)
def test_stealthintercept(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netids _time={{ epoch }} sourcetype="StealthINTERCEPT" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1



testdata2 = [
    '{{ mark }}{{ bsd }} NumberOfLogins=15801 UsedLoginProtocols=NTLM AttackingHost= AttackingHostIp= AttackedHost= AttackedHostIp= AlertText=Activity still in process.Account Sid: S-1-5-21-1740863675-3465329846-2508926007-106822; Account Name: TST\\xxx; Attack started: 3/11/2022 12:47:00 PM; Last activity: 3/11/2022 7:47:00 PM; Number of attempts: 15801; Number of attacking hosts: 8; Attacking hosts:  (UNKNOWN) 10.20.2.50 (6324), DC3PCDC01.XXX.XXX.CORP (2), AFAHEEM (1097), SB9PDUO01 (4), {{ host }}.TST.TSTUSA.CORP (8), SMITHLAPTOP (2), NYP2PCDC01.TST.XXX.CORP (24), PC6PDUO01 (5)',
]


@pytest.mark.addons("stealthwatch")
@pytest.mark.parametrize("event", testdata2)
def test_stealthintercept_alerts(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netids _time={{ epoch }} sourcetype="StealthINTERCEPT:alerts" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1