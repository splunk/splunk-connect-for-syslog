# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import re

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

import pytest

test_data = [
    {
        "orig": "<166>2014-05-20 00:54:44.627 -0700  WAF1 SYS ADMIN_M ALER 51001 Account has been locked for user Kevin because the number of consecutive log-in failures exceeded the maximum allowed",
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} ADMIN_M ALER 51001 Account has been locked for user Kevin because the number of consecutive log-in failures exceeded the maximum allowed",
        "log_type": "SYS",
        "sourcetype": "barracuda:system",
        "index": "netwaf"
    },
    {
        "orig": "<166>2014-04-11 10:50:30.411 +0530  wafbox1 WF ALER PRE_1_0_REQUEST 99.99.1.117 34006 99.99.109.2 80 global GLOBAL LOG NONE [POST /index.cgi] POST 99.99.109.2/index.cgi HTTP REQ-0+RES-0 “Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0”  99.99.1.117 34005 Kevin http://99.99.109.2/index.cgi",
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} ALER PRE_1_0_REQUEST 99.99.1.117 34006 99.99.109.2 80 global GLOBAL LOG NONE [POST /index.cgi] POST 99.99.109.2/index.cgi HTTP REQ-0+RES-0 “Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0”  99.99.1.117 34005 Kevin http://99.99.109.2/index.cgi",
        "log_type": "WF",
        "sourcetype": "barracuda:waf",
        "index": "netwaf"
    },
    {
        "orig": "<166>2014-04-11 12:11:24.964 +0530  wafbox1 TR 2001::1:109 80 2001::117 43740 \"-\" \"-\" GET HTTP 2001::1:109 HTTP/1.1 200 2837 232 0 1008 2001::117 80 10 REQ-0+RES-0   SERVER DEFAULT PASSIVE VALID /index.html name=srawat http://2001::1:109/index.cgi namdksih=askdj \"Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0\" 2001::117 43740 John gzip,deflate 2001::128 keep-alive",
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} 2001::1:109 80 2001::117 43740 \"-\" \"-\" GET HTTP 2001::1:109 HTTP/1.1 200 2837 232 0 1008 2001::117 80 10 REQ-0+RES-0   SERVER DEFAULT PASSIVE VALID /index.html name=srawat http://2001::1:109/index.cgi namdksih=askdj \"Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0\" 2001::117 43740 John gzip,deflate 2001::128 keep-alive",
        "log_type": "TR",
        "sourcetype": "barracuda:web",
        "index": "netwaf"
    },
    {
        "orig": "<166>v=2014-02-24 09:05:17.764 -0800  wafbox1 AUDIT Adam GUI 10.11.18.121 24784 CONFIG 166 config SET virtual_ip_config_address 99.99.130.45 virtual_ip_config_interface \"\" \"WAN\" []",
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} Adam GUI 10.11.18.121 24784 CONFIG 166 config SET virtual_ip_config_address 99.99.130.45 virtual_ip_config_interface \"\" \"WAN\" []",
        "log_type": "AUDIT",
        "sourcetype": "barracuda:audit",
        "index": "netwaf"
    },
    {
        "orig": "<166>2014-05-20 00:56:42.195 -0700  WAF1 NF INFO TCP 99.99.1.117 52676 99.99.79.2 80 ALLOW testacl MGMT/LAN/WAN interface traffic:allow",
        "template": "{{ mark }}{{ iso }}  {{ host }} {{ log_type }} INFO TCP 99.99.1.117 52676 99.99.79.2 80 ALLOW testacl MGMT/LAN/WAN interface traffic:allow",
        "log_type": "NF",
        "sourcetype": "barracuda:firewall",
        "index": "netwaf"
    }
]

env = Environment()

@pytest.mark.parametrize("test_case", test_data)
def test_barracuda_waf(
        record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, test_case
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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
