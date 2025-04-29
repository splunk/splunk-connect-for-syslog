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

test_rfc5424 = [
    r'{{ mark }}1 {{ iso }} {{ host }} aer01-abc-cde-fgh 0 711603 - "adf":1,"virtualservice":"virtualservice-12345-678-9810-b456-123456","vs_ip":"10.0.0.1","client_ip":"10.0.0.1","client_src_port":123,"client_dest_port":123,"start_timestamp":"2020-05-07T14:11:52.550629Z","report_timestamp":"2020-05-07T14:11:52.550629Z","connection_ended":1,"mss":1500,"rx_bytes":99,"rx_pkts":1,"service_engine":"aer01-abc-cde-fgh","log_id":711603,"server_ip":"0.0.0.0","server_conn_src_ip":"0.0.0.0","significant_log":["ADF_CLIENT_DNS_FAILED_GS_DOWN"],"dns_fqdn":"abc-cde-efg.cisco.com","dns_qtype":"DNS_RECORD_A","gslbservice":"gslbservice-xyz","gslbservice_name":"Naga-GSLB","dns_etype":"DNS_ENTRY_GSLB","protocol":"PROTOCOL_UDP","dns_request":{"question_count":1,"identifier":12345},"vs_name":"aer01-abc-cde-fgh"'
]
test_data_rfc = [
    r'{{ mark }}{{ date }} {{ avi_time }} {{ host }} Avi-Controller - - - INFO [abc-cde.gen: reason: Syslog for Confiqg Events occured] At 2020-04-07 15:27:10+00:00 event USER_AUTHORIZED_BY_RULE occurred on object abc-cde.gen in tenant admin as User abc-cde.gen was authorized by mapping rule user is member of groups "["abcd-efgh-ij-klmn"]" and ignore user attribute values.'
]
test_data_JSON = [
    r'{{ mark }}{{ date }} {{ avi_time }} {{ host }} Avi-Controller - - - INFO [abc-cde.gen: reason: Syslog for Config Events occured] {"level": "ALERT_LOW", "timestamp": "2020-04-07 15:35:26", "obj_name": "abc-cde.gen", "tenant_uuid": "admin", "summary": "Syslog for Config Events occured", "obj_key": "abc-cde.gen", "reason": "threshold_exceeded", "obj_uuid": "abc-cde.gen", "related_objects": [""], "threshold": 0, "events": [{"obj_type": "USER", "tenant_name": "", "event_id": "USER_AUTHORIZED_BY_RULE", "related_uuids": ["abc-cde.gen"], "event_details": {"config_user_authrz_rule_details": {"roles": "readonly-all", "tenants": "All Tenants", "user": "abc-cde.gen", "rule": "user is member of groups \"[\"abcd-efgh-ij-klmn\"]\" and ignore user attribute values"}}, "event_description": "User abc-cde.gen was authorized by mapping rule user is member of groups \"[\"abcd-efgh-ij-klmn\"]\" and ignore user attribute values", "module": "CONFIG", "report_timestamp": "2020-04-07 15:35:26", "internal": "EVENT_EXTERNAL", "event_pages": ["EVENT_PAGE_AUDIT", "EVENT_PAGE_ALL"], "context": "EVENT_CONTEXT_CONFIG", "obj_name": "abc-cde.gen", "obj_uuid": "abc-cde.gen", "tenant": "admin"}], "name": "abc-syslog"}'
]
test_data_no_host = [
    r'{{ mark }} {{ bsd }} {{ host }} [{{ date }} {{ avi_time }}: Avi-Controller: INFO: ] [abc-cde.gen: reason: Syslog for Config Events occured] At 2020-04-07 15:32:09+00:00 event USER_AUTHORIZED_BY_RULE occurred on object abc-cde.gen in tenant admin as User abc-cde.gen was authorized by mapping rule user is member of groups "["abcd-efgh-ij-klmn"]" and ignore user attribute values. {{ host }} '
]


@pytest.mark.addons("avi")
@pytest.mark.parametrize("event", test_data_rfc)
def test_avi_event_rfc(
    record_property,  setup_splunk, setup_sc4s, get_host_key, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)
    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]

    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, host=host, date=date, avi_time=avi_time)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="avi:events"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("avi")
@pytest.mark.parametrize("event", test_data_JSON)
def test_avi_event_json(
    record_property,  setup_splunk, setup_sc4s, get_host_key, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, host=host, date=date, avi_time=avi_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="avi:events"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("avi")
@pytest.mark.parametrize("event", test_data_no_host)
def test_avi_event_no_host(
    record_property,  setup_splunk, setup_sc4s, get_host_key, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, date=date, avi_time=avi_time, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops  sourcetype="avi:events" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("avi")
@pytest.mark.parametrize("event", test_rfc5424)
def test_avi_event_rfc5424(
    record_property,  setup_splunk, setup_sc4s, get_host_key, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<134>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string('search _time={{ epoch }} index=netops  sourcetype="avi:logs"')
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
