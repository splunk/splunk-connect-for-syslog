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

# <110>Jan 31 19:43:24 APM00243620939-B [358]: 2025-01-31T19:43:17 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id="2341" user="admin" resource_type="login_session" action="None" client_ip="10.114.173.252" appliance="APM00243620939" status="success"] User "admin" logged in successfully.
# <110>Jan 31 19:44:44 APM00243620939-B [358]: 2025-01-31T19:44:31 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id="2342" user="EncryptHTTP.PSb8ad27c26647" resource_type="login_session" action="None" client_ip="None" appliance="APM00243620939" status="success"] Successfully authenticated cert_account : Dell EMC PowerStore CA P9XEU8F5/EncryptHTTP.PSb8ad27c26647.
# <110>Jan 31 19:45:44 APM00243620939-B [358]: 2025-01-31T19:45:29 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Service [PowerStore_audit_event@1139 id="2347" user="root" resource_type="unknown" action="not applicable" client_ip="not applicable" appliance="APM00243620939" status="success"] User root executed the service script command [/cyc_host/cyc_service/bin/svc_diag list --hardware --sub_options firmware] from APM00243620939-A via shell.
# <110>Jan 31 19:48:25 APM00243620939-B [358]: 2025-01-31T19:48:16 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id="2349" user="EncryptHTTP.PSb8ad27c26647" resource_type="login_session" action="None" client_ip="None" appliance="APM00243620939" status="success"] Successfully authenticated cert_account : Dell EMC PowerStore CA P9XEU8F5/EncryptHTTP.PSb8ad27c26647.
# <110>Jan 31 19:49:05 APM00243620939-B [358]: 2025-01-31T19:48:49 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Config [PowerStore_audit_event@1139 id="2351" user="admin" resource_type="system_health_check" action="create" client_ip="10.114.173.252" appliance="APM00243620939" status="failed"] Failed to perform system health check on pki-tech-ps-p01.
# <110>Jan 31 19:58:46 APM00243620939-B [358]: 2025-01-31T19:58:22 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 Logout [PowerStore_audit_event@1139 id="2352" user="admin" resource_type="login_session" action="delete" client_ip="10.114.173.252" appliance="APM00243620939" status="success"] User "admin" was successfully logged out.
# <110>Jan 31 19:58:46 APM00243620939-B [358]: 2025-01-31T19:58:22 APM00243620939-B PSb8ad27c26647 358@HM3CTZ3 AlertEvent [PowerStore_remote_logging_alert@1139 sequence_number="52497" event_name="REMOTE_SUPPORT_CONNECTIVITY_STATUS_NORMAL" resource_type="remote_support" resource_name="SupportAssist" alert_id="ef7b021c-23a0-4821-8245-289cbdc7addd" alert_state="Cleared" appliance_name="rzpowerstore01-appliance-1" event_id="b320f9b7-c44e-bd39-ab56-8d278c69f6bb" event_code="0x00d00203" system_impact="None" repair_flow=""] Cluster connectivity is good. Appliance status: A1 Good.

test_cases = [
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id=\"2341\" user=\"admin\" resource_type=\"login_session\" action=\"None\" client_ip=\"10.114.173.252\" appliance=\"APM00243620939\" status=\"success\"] User \"admin\" logged in successfully.",
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id=\"2342\" user=\"EncryptHTTP.PSb8ad27c26647\" resource_type=\"login_session\" action=\"None\" client_ip=\"None\" appliance=\"APM00243620939\" status=\"success\"] Successfully authenticated cert_account : Dell EMC PowerStore CA P9XEU8F5/EncryptHTTP.PSb8ad27c26647.",
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Service [PowerStore_audit_event@1139 id=\"2347\" user=\"root\" resource_type=\"unknown\" action=\"not applicable\" client_ip=\"not applicable\" appliance=\"APM00243620939\" status=\"success\"] User root executed the service script command [/cyc_host/cyc_service/bin/svc_diag list --hardware --sub_options firmware] from APM00243620939-A via shell.",
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Authentication [PowerStore_audit_event@1139 id=\"2349\" user=\"EncryptHTTP.PSb8ad27c26647\" resource_type=\"login_session\" action=\"None\" client_ip=\"None\" appliance=\"APM00243620939\" status=\"success\"] Successfully authenticated cert_account : Dell EMC PowerStore CA P9XEU8F5/EncryptHTTP.PSb8ad27c26647.",
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Config [PowerStore_audit_event@1139 id=\"2351\" user=\"admin\" resource_type=\"system_health_check\" action=\"create\" client_ip=\"10.114.173.252\" appliance=\"APM00243620939\" status=\"failed\"] Failed to perform system health check on pki-tech-ps-p01.",
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 Logout [PowerStore_audit_event@1139 id=\"2352\" user=\"admin\" resource_type=\"login_session\" action=\"delete\" client_ip=\"10.114.173.252\" appliance=\"APM00243620939\" status=\"success\"] User \"admin\" was successfully logged out."
    "{{ mark }}{{ bsd }} {{ host }} [358]: {{ iso }} {{ host }} PSb8ad27c26647 358@HM3CTZ3 AlertEvent [PowerStore_remote_logging_alert@1139 sequence_number=\"52497\" event_name=\"REMOTE_SUPPORT_CONNECTIVITY_STATUS_NORMAL\" resource_type=\"remote_support\" resource_name=\"SupportAssist\" alert_id=\"ef7b021c-23a0-4821-8245-289cbdc7addd\" alert_state=\"Cleared\" appliance_name=\"rzpowerstore01-appliance-1\" event_id=\"b320f9b7-c44e-bd39-ab56-8d278c69f6bb\" event_code=\"0x00d00203\" system_impact=\"None\" repair_flow=\"\"] Cluster connectivity is good. Appliance status: A1 Good."
]


@pytest.mark.parametrize("case", test_cases)
@pytest.mark.addons("dell")
def test_dell_powerstore(
    record_property, setup_splunk, setup_sc4s, case
):
    host = f'test-dell-powerstore-{test_cases.index(case)}'

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(case + "\n")
    message = mt.render(mark="<110>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="dell:emc:powerstore" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
