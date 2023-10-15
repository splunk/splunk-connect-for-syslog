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

# https://www.ciscolive.com/c/dam/r/ciscolive/us/docs/2017/pdf/TECUCC-3000.pdf

test_device_connector = [
    r'{{mark}} {{bsd}} {{ host }} hx-device-connector: 433   Running job task        {"traceId": "AS44b5d3f67f8b7d1911a2615bde31b566", "traceId": "DCJOBf51022fbb9992e2623cdb1f415bdb838", "jobName": "duracell:health"}'
]
# <13>Oct 26 09:22:27.524 hostname hx-ssl-access: - - [26/Oct/2020:17:22:26 +0800] "GET /coreapi/v1/clusters/000000:0000000/alarms HTTP/1.1" 200 2 "-" "Go-http-client/1.1"
test_audit_data = [
    r"{{mark}} {{bsd}} {{ host }} hx-audit-rest: 22:26.678 - PERFORMANCE TRACE - HxSvcMgrClient.getHxClusterIdentifier -> 4 ms"
]
test_ssl_data = [
    r'{{mark}} {{bsd}} {{ host }} hx-ssl-access: - - [26/Oct/2020:17:22:26 +0800] "GET /coreapi/v1/clusters/000000:0000000/alarms HTTP/1.1" 200 2 "-" "Go-http-client/1.1"'
]


@pytest.mark.parametrize("event", test_device_connector)
@pytest.mark.addons("cisco")
def test_cisco_ucs_hyperflex(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="cisco:ucs:hx"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", test_audit_data)
@pytest.mark.addons("cisco")
def test_cisco_ucs_hyperflex_audit(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="cisco:ucs:hx"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", test_ssl_data)
@pytest.mark.addons("cisco")
def test_cisco_ucs_hyperflex_ssl(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }}  sourcetype="cisco:ucs:hx"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
