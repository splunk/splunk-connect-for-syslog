# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime

import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))

# Example raw log message as emitted by Thales STA (RFC6587 octet-counted
# framing, RFC5424 header with a UTF-8 BOM in place of the nil SDATA, and a
# multi-line pretty-printed JSON body):
#
#   689 <14>1 2025-02-20T15:48:44.978773+00:00 sta.example.com - - RemoteLogging \ufeff{
#     "logVersion": "1.0",
#     "category": "AUDIT",
#     "timeStamp": "2025-02-20T15:48:44.9787739Z",
#     "id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#     "context": {
#       "tenantId": "XXXXXXXXXX",
#       "originatingAddress": "12.345.6.789",
#       "principalId": "XXXXX",
#       "globalAccessId": "00000000-0000-0000-0000-000000000000"
#     },
#     "details": {
#       "type": "AUTHENTICATION",
#       "serial": "XXXXXXXXX",
#       "action": "0",
#       "actionText": "AUTH_ATTEMPT",
#       "result": "1",
#       "resultText": "AUTH_SUCCESS",
#       "agentId": "6",
#       "message": "",
#       "usedName": "XXXXX",
#       "credentialType": "GrIDsure"
#     }
#   }
STA_JSON_BODY = (
    "{\n"
    '  "logVersion": "1.0",\n'
    '  "category": "AUDIT",\n'
    '  "timeStamp": "2025-02-20T15:48:44.9787739Z",\n'
    '  "id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",\n'
    '  "context": {\n'
    '    "tenantId": "XXXXXXXXXX",\n'
    '    "originatingAddress": "12.345.6.789",\n'
    '    "principalId": "XXXXX",\n'
    '    "globalAccessId": "00000000-0000-0000-0000-000000000000"\n'
    "  },\n"
    '  "details": {\n'
    '    "type": "AUTHENTICATION",\n'
    '    "serial": "XXXXXXXXX",\n'
    '    "action": "0",\n'
    '    "actionText": "AUTH_ATTEMPT",\n'
    '    "result": "1",\n'
    '    "resultText": "AUTH_SUCCESS",\n'
    '    "agentId": "6",\n'
    '    "message": "",\n'
    '    "usedName": "XXXXX",\n'
    '    "credentialType": "GrIDsure"\n'
    "  }\n"
    "}"
)


@pytest.mark.addons("thales")
def test_thales_sta(
    record_property, get_host_key, setup_splunk, setup_sc4s
):
    """End-to-end test for the dedicated STA RFC6587_NOPARSE listener.

    STA advertises RFC5424 but emits a UTF-8 BOM in place of
    structured-data and prettifies the JSON body across many lines, framed
    with RFC6587 octet-counting. The ``RFC6587_NOPARSE`` listener
    (``SC4S_LISTEN_THALES_STA_RFC6587_NOPARSE_PORT``) accepts the frame
    as-is; the ``app-netsource-thales_sta`` parser then rebuilds the
    header, strips the BOM, and routes the JSON body to Splunk with
    ``index=netauth`` and ``sourcetype=thales:sta:json``.
    """
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-3]

    iso_sta = dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "+00:00"
    bom = "\ufeff"

    # STA omits the `-` for nil SDATA and places the BOM there instead, so
    # the header part is `... - - MSGID <BOM>{...body...}`.
    payload = (
        f"<14>1 {iso_sta} {host} - - RemoteLogging {bom}{STA_JSON_BODY}"
    )

    # RFC6587 octet-counted framing: "<length> <payload>" where <length>
    # is the UTF-8 byte length of the payload.
    payload_length = len(payload.encode("utf-8"))
    framed_message = f"{payload_length} {payload}"

    sendsingle(framed_message, setup_sc4s[0], setup_sc4s[1][9003])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" '
        'sourcetype="thales:sta:json" source="thales:sta" '
        'sta_source_name="RemoteLogging"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", payload)

    assert result_count == 1
