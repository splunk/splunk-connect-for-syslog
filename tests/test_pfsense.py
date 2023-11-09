# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <27>Jan 25 01:58:06 filterlog: 82,,,1000002666,mvneta2,match,pass,out,6,0x00,0x00000,64,ICMPv6,58,8,fe80::208:a2ff:fe0f:cb66,fe80::56a6:5cff:fe7d:1d43,
@pytest.mark.addons("pfsense")
def test_pfsense_filterlog(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} filterlog: 82,,,1000002666,mvneta2,match,pass,out,6,0x00,0x00000,64,ICMPv6,58,8,{{key}},\n"
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6000])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw sourcetype=pfsense:filterlog "{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <27>Jan 25 01:58:06 kqueue error: unknown
@pytest.mark.addons("pfsense")
def test_pfsense_other(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{mark}}{{ bsd }} kqueue error: {{key}}\n")
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6000])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=pfsense:* "{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <27>Jan 25 01:58:06 syslogd: restart
@pytest.mark.addons("pfsense")
def test_pfsense_syslogd(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{mark}}{{ bsd }} syslogd: restart {{key}}\n")
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6000])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=pfsense:syslogd "{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
