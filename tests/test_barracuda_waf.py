# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import re

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

# Log examples based on https://campus.barracuda.com/product/webapplicationfirewall/doc/92767349/exporting-log-formats/
test_data = [
    {
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} ADMIN_M ALER 51001 Account has been locked for user User because the number of consecutive log-in failures exceeded the maximum allowed",
        "log_type": "SYS",
        "sourcetype": "barracuda:system",
        "index": "netwaf"
    },
    {
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} ALER PRE_1_0_REQUEST 1.1.1.1 34006 1.1.1.2 80 global GLOBAL LOG NONE [POST /index.cgi] POST 1.1.1.2/index.cgi HTTP REQ-0+RES-0 “Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0”  1.1.1.117 34005 User http://1.1.1.2/index.cgi",
        "log_type": "WF",
        "sourcetype": "barracuda:waf",
        "index": "netwaf"
    },
    {
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} 1001::1:1 80 1001::1 43740 \"-\" \"-\" GET HTTP 1001::1:1 HTTP/1.1 200 2837 232 0 1008 1001::1 80 10 REQ-0+RES-0   SERVER DEFAULT PASSIVE VALID /index.html name=user http://1001::1:1/index.cgi namdksih=azkdz \"Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0\" 1001::117 43740 User gzip,deflate 1001::128 keep-alive",
        "log_type": "TR",
        "sourcetype": "barracuda:web",
        "index": "netwaf"
    },
    {
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} User GUI 1.1.1.121 24784 CONFIG 166 config SET virtual_ip_config_address 99.99.130.45 virtual_ip_config_interface \"\" \"WAN\" []",
        "log_type": "AUDIT",
        "sourcetype": "barracuda:audit",
        "index": "netwaf"
    },
    {
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} INFO TCP 1.1.1.117 52676 1.1.1.2 80 ALLOW testacl MGMT/LAN/WAN interface traffic:allow",
        "log_type": "NF",
        "sourcetype": "barracuda:firewall",
        "index": "netwaf"
    }
]


env = Environment(autoescape=select_autoescape(default_for_string=False))

@pytest.mark.parametrize("test_case", test_data)
@pytest.mark.addons("barracuda")
def test_barracuda_waf(
        record_property, get_host_key, setup_splunk, setup_sc4s, test_case
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso = dt.astimezone().isoformat(sep=" ", timespec="milliseconds")                 # '2023-07-19 11:45:48.819+00:00'
    vendor_iso_format = re.sub(r'(.+)([+-])(\d{2}):(\d{2})$', r'\1 \2\3\4', iso)      # '2023-07-19 11:45:48.819 +0000'

    mt = env.from_string(test_case["template"] + "\n")
    message = mt.render(mark="<134>", iso=vendor_iso_format, host=host, log_type=test_case["log_type"])

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    epoch = dt.astimezone().strftime("%s.%f")[:-3]
    st = env.from_string(
        'search index={{ index }} _time={{ epoch }} sourcetype={{ source_type }} host={{ host }}'
    )
    search = st.render(index=test_case["index"], epoch=epoch, source_type=test_case["sourcetype"], host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
