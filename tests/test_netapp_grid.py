# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

@pytest.mark.addons("netapp")
def test_netapp_test_audit_event(
        record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }}{{ bsd }} {{ host }} Audit: 2022-11-23T12:02:51.007373 [AUDT:[MRMD(CSTR):"POST"][MPAT(CSTR):"/api/v3/authorize"][MPQP(CSTR):""][MDNA(CSTR):"8.8.8.8"][MSIP(CSTR):"4.4.4.4"][MDIP(CSTR):"4.4.4.4"][MUUN(CSTR):""][MRSC(UI32):200][RSLT(FC32):SUCS][MRSP(CSTR):""][MRBD(CSTR):"{\"username\":\"root\",\"password\":\"********\",\"cookie\":\"true\",\"csrfToken\":\"false\"}"][AVER(UI32):10][ATIM(UI64):1669204971007373][ATYP(FC32):MGAU][ANID(UI32):12525832][AMID(FC32):GMGT][ATID(UI64):12690095365319551758]]'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<190>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="grid:auditlog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("netapp")
def test_netapp_test_restapi_event(
        record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }}{{ bsd }} {{ host }} NMS: {"MGAU":{"sourceIp":"4.4.4.4","destinationIp":"8.8.8.8","domainName":"8.8.8.8","requestMethod":"POST","requestBody":"{\"username\":\"root\",\"password\":\"********\",\"cookie\":\"true\",\"csrfToken\":\"false\"}","requestPath":"/api/v3/authorize","queryParameters":"","responseCode":200,"userURN":"","responseBody":"","forceCreate":true}}'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<38>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="grid:rest:api"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
