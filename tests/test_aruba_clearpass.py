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

test_data_cppm = [
    "{{ mark }}{{ aruba_time }} {{ host }} CPPM_System_Events 973 1 0 event_source=SnmpService,level=ERROR,category=Trap,description=Switch IP=10.17.8.67. Ignore v2c trap. Bad    security name in   trap,action_key=Failed,timestamp=2014-06-03 13:05:30.023+05:30",
    "{{ mark }}{{ aruba_time }} {{ host }} TEST filter 0 1 0 Common.Alerts=WebAuthService: User 'bbb' not present in [Local User Repository](localhost)User 'bbb' not present in ClearPass Lab AD(adisam.arubapoc.local),Common.Alerts-Present=0,Common.Audit-Posture-Token=UNKNOWN,Common.Auth-Type=,Common.Enforcement-Profiles=[Deny Application Access Profile],Common.Error-Code=201,Common.Host-MAC-   Address=,Common.Login-Status=REJECT,Common.Monitor-Mode=Enabled,Common.Request-Id=W0000002e-01-533557ec,Common.Request-Timestamp=2014-03-  28 16:37:24.417+05:30,Common.Roles=,Common.Service=EAI ClearPass Identity Provider (SAML IdP Service),Common.Source=Application,Common.System-Posture-Token=UNKNOWN,Common.Username=bbb,WEBAUTH.Auth-Source=,WEBAUTH.Host-IP-  Address=127.0.0.1,",
    "{{ mark }}{{ aruba_time }} {{ host }} All Session Log Fields 4 1 0 Common.Alerts-Present=0,Common.Audit-Posture-Token=UNKNOWN,Common.Auth-Type=,Common.Enforcement-Profiles=EAI ClearPass Identity Provider (SAML IdP Service) Profile,Common.Error-Code=0,Common.Host-MAC-   Address=,Common.Login-Status=ACCEPT,Common.Monitor-Mode=Disabled,Common.Request-Id=W00000032-01-  5335874b,Common.Request-Timestamp=2014-03-  28 19:59:31.533+05:30,Common.Roles=[Employee], [User Authenticated],Common.Service=EAI ClearPass Identity Provider (SAML IdP Service),Common.Source=Application,Common.System-Posture-Token=UNKNOWN,Common.Username=prem1,WEBAUTH.Auth-Source=[Local User Repository],WEBAUTH.Host-IP-  Address=127.0.0.1,",
    "{{ mark }}{{ aruba_time }} {{ host }} All Events 710 1 0 Timestamp=Mar 28, 2014 19:59:39 IST,Source=Endpoint Context Server,Level=ERROR,Category=MaaS360: Communication Error,Action=Failed,Description=Failed to fetch Endpoint details from MaaS360 - verify Proxy settings, Server credentials and retry.",
    "{{ mark }}{{ aruba_time }} {{ host }} All Audits 30 1 0 Timestamp=Mar 28, 2014 16:46:59 IST,Source=All Audits,Category=Syslog Export Data,Action=MODIFY,User=admin",
]


@pytest.mark.addons("aruba")
@pytest.mark.parametrize("event", test_data_cppm)
def test_aruba_clearpass_CPPM(
    record_property,  setup_splunk, setup_sc4s, get_host_key, event
):
    host = "aruba-cp-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    aruba_time = dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<46>", bsd=bsd, host=host, date=date, aruba_time=aruba_time
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="aruba:clearpass"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
