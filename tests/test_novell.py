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

testdata = [
    '{{mark}}{{ bsd }} {{ host }} {"appName":"Novell Access Manager","timeStamp":"{{device_time}}","eventId":"002E0009","subTarget":"c7620505dc4b61cca7665cf1c092ea9980af164691cc5adf88d104dfff18a315","stringValue1":"https://login-test.authbridge-nonprod.XXXgroup.com/nidp/saml2/metadata","stringValue2":"https://obp-sso-tst2.xxx.wbctestau.xxxx.com.au/oam/fed","stringValue3":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36-SCCrow32z","numericValue1":0,"numericValue2":0,"numericValue3":0,"originator":"C423618A1F3FB8F2","component":"nidp","data":"MTAuOTcuMTQ0LjE1Ng==","description":"NIDS: Provided an authentication to a remote consumer","message":"[Tue, 15 Jun 2021 02:35:28 +1000]  [Novell Access Manager\\\\nidp]: AMDEVICEID#C423618A1F3FB8F2: AMAUTHID#c7620505dc4b61cca7665cf1c092ea9980af164691cc5adf88d104dfff18a315: Provided an authentication to a remote consumer on behalf of user: [cn=xxxxx,ou=users,o=data]. Authentication Type: [https://login-test.authbridge-nonprod.XXXgroup.com/nidp/saml2/metadata] Authenticating Entity Name: [https://obp-sso-tst2.xxx.xxx.XXX.com.au/oam/fed] Contract Class or Method Name: [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36-SCCrow32z] Client IP Address: [10.0.0.0]","target":"cn=xxx,ou=users,o=data"}',
]
# Tue, 15 Jun 2021 02:35:28 +1000


@pytest.mark.addons("novell")
@pytest.mark.parametrize("event", testdata)
def test_data_access_manager(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]
    device_time = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<132>", bsd=bsd, host=host, device_time=device_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="novell:netiq"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="ossec")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
