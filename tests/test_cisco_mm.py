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


# <14>Jan 26 14:20:39 host cluster_audit: {"Timestamp" : "2022-01-26T14:19:27.512Z", "AttributeMap" : {}, "EntityType" : "Access Token", "EntityId" : "cohesitysnowdev", "EntityName" : "cohesitysnowdev", "User" : "", "Domain" : "local", "Action" : "Create", "Description" : "@local attempted to generate new access token for user cohesitysnowdev on domain local from 1.1.1.1 failed with error Invalid Username or Password specified.", "ClusterInfo" : "ClusterName: clustername, ClusterId: xxxxxx"}
testdata_sys = [
    '{{ mark }}{{ bsd }} {{ host }} cmm-web_smart_agent_1[273]:  INFO 2022-02-20T18:53:05.123456Z SUCCESS | initializing smart agent v1.2.5 | sapy.manage:19',
    '{{ mark }}{{ bsd }} {{ host }} cmm-web_proxy_1[273]:  Web is available - starting',
    '{{ mark }}{{ bsd }} {{ host }} cmm-web_events_monitor_1[273]:  2022-02-20 18:54:16,460 - INFO - 154:123456789012345 - /home/unprivuser/cmm/cmm_meetings/management/commands/run_events_handler.py:38 - Handler for mycmsserver01 (2) started',
]

testdata_audit = [
    '{{ mark }}{{ bsd }} {{ host }} 2022-02-20  18:52:22,250 - local:myuser/HTTP/IPv3:1.2.3.4:tcp:50010 - Update configuration successful',
]


@pytest.mark.parametrize("event", testdata_sys)
@pytest.mark.addons("cisco")
def test_cisco_mm_sys(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="cisco:mm:system:*" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_sys)
@pytest.mark.addons("cisco")
def test_cisco_mm_sys2(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test-cisco-mm-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="cisco:mm:system:*" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

@pytest.mark.parametrize("event", testdata_audit)
@pytest.mark.addons("cisco")
def test_cisco_mm_audit(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test-cisco-mm-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="cisco:mm:audit" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
