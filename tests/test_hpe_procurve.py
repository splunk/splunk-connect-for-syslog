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
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <46> May 15 14:04:23 192.168.1.254  00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode
testdata = [
    r"{{ mark }} {{bsd}} {{host}} 00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode",
    r"{{ mark }} {{bsd}} {{host}}  00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode",
]


@pytest.mark.addons("hp")
@pytest.mark.parametrize("event", testdata)
def test_hpe_procurve_fmt2(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>", host=host, bsd=bsd)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="hpe:procurve"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#%%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched
# <189>Jan 27 14:13:39 2022 host (Stack) %%10WEB/5/LOGIN: admin-af@example.local logged in from 10.0.0.0..
testdata_alt1 = [
    r"{{ mark }} {{bsd}} {{host}} %%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched",
    r"{{ mark }} {{bsdyear}} {{host}} %%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched",
    r"{{ mark }} {{bsd}} {{host}} (Stack) %%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched",
    r"{{ mark }} {{bsdyear}} {{host}} (Stack) %%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched",
]


@pytest.mark.addons("hp")
@pytest.mark.parametrize("event", testdata_alt1)
def test_hpe_procurve_fmt1(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(
        mark="<29>", host=host, bsd=bsd, bsdyear=dt.strftime("%b %d %H:%M:%S %Y")
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="hpe:procurve"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
