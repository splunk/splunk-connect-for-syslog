# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *
import pytest
import datetime

env = Environment()


# <46> May 15 14:04:23 192.168.1.254  00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode
testdata = [
    r"{{ mark }} {{bsd}} {{host}} 00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode",
    r"{{ mark }} {{bsd}} {{host}}  00179 mgr:  SME SSH from 192.168.1.22 - MANAGER Mode",
]
#%%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched
testdata_alt1 = [
    r"{{ mark }} {{bsd}} {{host}} %%10SC/6/SC_AAA_LAUNCH(l): -AAAType=AUTHEN-AAAScheme= local-Service=login-UserName=admin@system; AAA launched",
]


@pytest.mark.parametrize("event", testdata)
def test_hpe_procurve(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>", host=host, bsd=bsd)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="hpe:procurve"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@pytest.mark.parametrize("event", testdata_alt1)
def test_hpe_procurve_alt1(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>", host=host, bsd=bsd)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="hpe:procurve"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
