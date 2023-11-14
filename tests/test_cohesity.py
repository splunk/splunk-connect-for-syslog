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
testdata = [
    '{{ mark }}{{ bsd }} {{ host }} cluster_audit: {"Timestamp" : "{{ iso }}", "AttributeMap" : {}, "EntityType" : "Access Token", "EntityId" : "cohesitysnowdev", "EntityName" : "cohesitysnowdev", "User" : "", "Domain" : "local", "Action" : "Create", "Description" : "@local attempted to generate new access token for user cohesitysnowdev on domain local from 1.1.1.1 failed with error Invalid Username or Password specified.", "ClusterInfo" : "ClusterName: clustername, ClusterId: xxxxxx"}',
]

@pytest.mark.addons("cohesity")
@pytest.mark.parametrize("event", testdata)
def test_cohesity_cluster_audit(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="cohesity:cluster:audit" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <14>Jan 26 14:20:39 host cluster_audit: {"Timestamp" : "2022-01-26T14:19:27.512Z", "AttributeMap" : {}, "EntityType" : "Access Token", "EntityId" : "cohesitysnowdev", "EntityName" : "cohesitysnowdev", "User" : "", "Domain" : "local", "Action" : "Create", "Description" : "@local attempted to generate new access token for user cohesitysnowdev on domain local from 1.1.1.1 failed with error Invalid Username or Password specified.", "ClusterInfo" : "ClusterName: clustername, ClusterId: xxxxxx"}
testdata2 = [
    '{{ mark }}{{ bsd }} {{ host }} dataprotection_events: {"EventMessage" : "Expiring backup run", "Timestamp" : "{{ iso }}", "ClusterInfo" : {"ClusterId" : "1755240360407376", "ClusterName" : "cluster-name"}, "EventType" : "kBackup", "EnvironmentType" : "kVMware", "RegisteredSource" : {"EntityType" : "kVMware", "EntityId" : "1", "EntityName" : "ttllxapp-vc01"}, "BackupJobName" : "test1", "BackupJobId" : "582", "Entities" : [{"EntityType" : "kVMware", "EntityId" : "27", "EntityName" : "xxx-xxx"}, {"EntityType" : "kVMware", "EntityId" : "70", "EntityName" : "ttllxapp-joe01"}], "TaskId" : "509872", "AttributeMap" : {}}',
]


@pytest.mark.addons("cohesity")
@pytest.mark.parametrize("event", testdata2)
def test_cohesity_dataprotection_events(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="cohesity:cluster:dataprotection" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_api_audit = [
    '{{ mark }}{{ iso }} {{ host }} api_audit[{{ pid }}]: {"username":"admin","domain":"LOCAL","method":"GET","urlPath":"/","requestTimestamp":1696526790076,"statusCode":200,"responseHeader":{"Cache-Control":["no-cache, no-store, must-revalidate"],"Content-Encoding":["gzip"],"Content-Type":["application/json"],"Pragma":["no-cache"],"Referrer-Policy":["strict-origin-when-cross-origin"],"Strict-Transport-Security":["max-age=31536000; includeSubDomains"],"Vary":["Accept-Encoding"],"X-Content-Type-Options":["nosniff"],"X-Frame-Options":["SAMEORIGIN"],"X-Ratelimit-Limit":["10000"],"X-Ratelimit-Remaining":["9998"],"X-Ratelimit-Reset":["1696526790"],"X-Xss-Protection":["1; mode=block"]},"responseTime":156705634}'
]


@pytest.mark.addons("cohesity")
@pytest.mark.parametrize("event", testdata_api_audit)
def test_cohesity_api_audit(
    record_property,  get_host_key, get_pid, setup_splunk, setup_sc4s, event
):
    host = get_host_key
    pid = get_pid

    dt = datetime.datetime.now()
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<14>", host=host, iso=iso, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=infraops _time={{ epoch }} sourcetype="cohesity:api:audit" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
