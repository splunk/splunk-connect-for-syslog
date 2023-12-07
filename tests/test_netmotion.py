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

data = [
    r'{{ mark }} {{ iso }}Z {{ host }} nmreporting.exe 7596 PoolStatus [nm_pool_status@11912 d_count="25" d_count_android="8" d_count_ios="17" d_count_mac="0" d_count_win="0" d_license_avail="175" d_license_tot="200" pool_name="mobility" rep_disabled="1"]',
]


@pytest.mark.addons("netmotion")
@pytest.mark.parametrize("event", data)
def test_netmotion_reporting(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="netmotion:reporting"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# sample from https://help.netmotionsoftware.com/support/docs/Diagnostics/410/help/DiagnosticsHelp.htm#page/NetMotion%20Diagnostics%20Help/exporting.14.11.html#ww1002396
datamobilityserver = [
    r'{{ mark }} {{ iso }}Z {{ host }} LocalityServer - - [nm_MobilityAnalyticsAppData@11912 MobilityPID="01BF47AA41BDE17800505995159C002" DeviceName="Wemmet-5547" UserName="tim.smith" PhoneNumber="2065551234" CurrentCarrier="AT&T" AppName="CustomApp1" AppType="User" Bytes="1116842" DateHour="2017-02-26T19:00:00.000Z"]',
]


@pytest.mark.addons("netmotion")
@pytest.mark.parametrize("event", datamobilityserver)
def test_netmotion_mobilityserver(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="netmotion:mobilityserver:nm_mobilityanalyticsappdata"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
