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


# <101> April 04 21:03:05 AirWatch  AirWatch Syslog Details are as follows Event Type: DeviceEvent: SecurityInformationConfirmedUser: sysadminEvent Source: DeviceEvent Module: DevicesEvent Category: CommandEvent Data: Device: Schalueck Marc DUS Project Leader iPad DMPD6548Q1GCUser: sysadmin EnrollmentUser: Schalueck Marc Event Timestamp: April 4, 2022 21:03:04



testdata_admin = [
    '{{ mark }} {{ bsd }} AirWatch  AirWatch Syslog Details are as follows Event Type: DeviceEvent: SecurityInformationConfirmedUser: sysadminEvent Source: DeviceEvent Module: DevicesEvent Category: CommandEvent Data: Device: Schalueck Marc DUS Project Leader iPad DMPD6548Q1GCUser: sysadmin EnrollmentUser: Schalueck Marc Event Timestamp: {{ bsd_airwatch }}'
]


@pytest.mark.parametrize("event", testdata_admin)
@pytest.mark.addons("vmware")
def test_airwatch(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)
    bsd_airwatch = dt.strftime("%B %d, %Y %H:%M:%S")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<101>", bsd=bsd, host=host, date=date, bsd_airwatch=bsd_airwatch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=epintel sourcetype="vmware:airwatch" '
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
