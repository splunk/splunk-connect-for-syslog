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

test_rfc5424 = [r'{{ mark }}1 {{ iso }} {{ host }} aer01-stg-int-ns1 0 711603 - "adf":1,"virtualservice":"virtualservice-70fda850-75a8-4f0d-b973-5d2460a7b53d","vs_ip":"144.254.64.10","client_ip":"173.37.142.74","client_src_port":20032,"client_dest_port":53,"start_timestamp":"2020-05-07T14:11:52.550629Z","report_timestamp":"2020-05-07T14:11:52.550629Z","connection_ended":1,"mss":1500,"rx_bytes":99,"rx_pkts":1,"service_engine":"aer01-stg-int-se-csfjq","log_id":711603,"server_ip":"0.0.0.0","server_conn_src_ip":"0.0.0.0","significant_log":["ADF_CLIENT_DNS_FAILED_GS_DOWN"],"dns_fqdn":"naga-gslb-p3.avi-svl-internal.cisco.com","dns_qtype":"DNS_RECORD_A","gslbservice":"gslbservice-1eda07e5-33f2-457f-92ec-a6b3d95992e1","gslbservice_name":"Naga-GSLB","dns_etype":"DNS_ENTRY_GSLB","protocol":"PROTOCOL_UDP","dns_request":{"question_count":1,"identifier":61695},"vs_name":"aer01-stg-int-ns1"']
test_data_rfc = [r'{{ mark }}{{date }} {{ avi_time }} {{ host }} Avi-Controller - - - INFO [dc-um-monitor.gen: reason: Syslog for Config Events occured] At 2020-04-07 15:27:10+00:00 event USER_AUTHORIZED_BY_RULE occurred on object dc-um-monitor.gen in tenant admin as User dc-um-monitor.gen was authorized by mapping rule user is member of groups "["dcnet-genericid-ro-arbac"]" and ignore user attribute values.']
test_data_JSON = [r'{{ mark }}{{date }} {{ avi_time }} {{ host }} Avi-Controller - - - INFO [dc-um-monitor.gen: reason: Syslog for Config Events occured] {"level": "ALERT_LOW", "timestamp": "2020-04-07 15:35:26", "obj_name": "dc-um-monitor.gen", "tenant_uuid": "admin", "summary": "Syslog for Config Events occured", "obj_key": "dc-um-monitor.gen", "reason": "threshold_exceeded", "obj_uuid": "dc-um-monitor.gen", "related_objects": [""], "threshold": 0, "events": [{"obj_type": "USER", "tenant_name": "", "event_id": "USER_AUTHORIZED_BY_RULE", "related_uuids": ["dc-um-monitor.gen"], "event_details": {"config_user_authrz_rule_details": {"roles": "readonly-all", "tenants": "All Tenants", "user": "dc-um-monitor.gen", "rule": "user is member of groups \"[\"dcnet-genericid-ro-arbac\"]\" and ignore user attribute values"}}, "event_description": "User dc-um-monitor.gen was authorized by mapping rule user is member of groups \"[\"dcnet-genericid-ro-arbac\"]\" and ignore user attribute values", "module": "CONFIG", "report_timestamp": "2020-04-07 15:35:26", "internal": "EVENT_EXTERNAL", "event_pages": ["EVENT_PAGE_AUDIT", "EVENT_PAGE_ALL"], "context": "EVENT_CONTEXT_CONFIG", "obj_name": "dc-um-monitor.gen", "obj_uuid": "dc-um-monitor.gen", "tenant": "admin"}], "name": "Syslog-Config-Events-dc-um-monitor.gen-1586273726.95-1586273726-1855152"}']
test_data_no_host = [r'{{ mark }}[{{date }} {{ avi_time }}: Avi-Controller: INFO: ] [dc-um-monitor.gen: reason: Syslog for Config Events occured] At 2020-04-07 15:32:09+00:00 event USER_AUTHORIZED_BY_RULE occurred on object dc-um-monitor.gen in tenant admin as User dc-um-monitor.gen was authorized by mapping rule user is member of groups "["dcnet-genericid-ro-arbac"]" and ignore user attribute values.']

@pytest.mark.parametrize("event", test_data_rfc)
def test_avi_event_rfc(
        record_property, setup_wordlist, setup_splunk, setup_sc4s, get_host_key, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]

    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, host=host, date=date, avi_time=avi_time)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="avi:events"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@pytest.mark.parametrize("event", test_data_JSON)
def test_avi_event_JSON(
        record_property, setup_wordlist, setup_splunk, setup_sc4s, get_host_key, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, host=host, date=date, avi_time=avi_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="avi:events"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@pytest.mark.parametrize("event", test_data_no_host)
def test_avi_event_no_host(
        record_property, setup_wordlist, setup_splunk, setup_sc4s, get_host_key, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    avi_time = dt.strftime("%H:%M:%S,%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<46>", bsd=bsd, date=date, avi_time=avi_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main  sourcetype="avi:events"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@pytest.mark.parametrize("event", test_rfc5424)
def test_avi_event_rfc5424(record_property, setup_wordlist, setup_splunk, setup_sc4s, get_host_key, event):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<134>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        'search _time={{ epoch }} index=main  sourcetype="avi:logs"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1