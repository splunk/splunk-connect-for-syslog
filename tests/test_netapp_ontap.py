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


testdata = [
    "{{ mark }}{{ bsd }} {{ host }}: {{ host }}: 00000030.00c8f1e2 11e5347f {{ device_time }} [kern_audit3167] 8004b7000021e73b:4005f7000021e73d :: cluster:ssh :: 0.0.0.0:32879 :: cluster:admin :: qos statistics volume performance show -rows 20 -iter 1 :: Pending",
]

# <14>Oct 3 11:36:46 host: host: 00000030.00c8f1e2 11e5347f Thu Oct 03 2024 11:36:44 -06:00 [kern_audit3167] 8004b7000021e73b:4005f7000021e73d :: cluster:ssh :: 0.0.0.0:32879 :: cluster:admin :: qos statistics volume performance show -rows 20 -iter 1 :: Pending
@pytest.mark.addons("netapp")
@pytest.mark.parametrize("event", testdata)
def test_netapp_ontap_audit(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "netapp-ontap-" + get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    # Wed Jun 23 2021 22:09:18 +10:00
    device_time = dt.strftime("%a %b %d %Y %H:%M:%S +00:00")

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<14>", bsd=bsd, host=host, device_time=device_time)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="netapp:ontap:ems"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Netapp Ontap EMS event in rfc5424 format
# <5>1 2024-10-03T07:54:02-06:00 host program - wafl.scan.done - Completed Volume Footprint Estimator Scan on volume vm_unix002_0d@vserver:27902083bf98-11e9-87fe-00a098b15eb6
@pytest.mark.addons("netapp")
def test_netapp_ontap_ems_rfc5424(
        record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = "netapp-ontap-" + get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} program - wafl.scan.done - Completed Volume Footprint Estimator Scan on volume vm_unix002_0d@vserver:27902083bf98-11e9-87fe-00a098b15eb6'
    )
    message = mt.render(mark="<5>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops sourcetype="netapp:ontap:ems"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1