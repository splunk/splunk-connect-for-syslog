# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import uuid
import random
import pytz

from jinja2 import Environment, environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
import uuid
from .timeutils import time_operations
import datetime

env = Environment()

# <12> 01/10/2001:01:01:01 GMT netscaler ABC-D : SSLVPN HTTPREQUEST 1234567 : Context username@192.0.2.1 - SessionId: 12345- example.com User username : Group(s) groupname : Vserver a1b2:c3d4:e5f6:a7b8:c9d0:e1f2:a3b4:c5d6:123 - 01/01/2001:01:01:01 GMT GET file/path.gif - -
def test_citrix_netscaler(record_property,  setup_splunk, setup_sc4s):
    host = f"test-ctitrixns-host-{uuid.uuid4().hex}"
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ time }} GMT {{ host }} ABC-D : SSLVPN HTTPREQUEST 1234567 : Context username@192.0.2.1 - SessionId: 12345- example.com User username : Group(s) groupname : Vserver a1b2:c3d4:e5f6:a7b8:c9d0:e1f2:a3b4:c5d6:123 - 01/01/2001:01:01:01 GMT GET file/path.gif - -\n"
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <134>Jun 18 18:18:42 svm_service: 1.1.1.1  18/06/2020:16:18:42 GMT mynetscaler2 0-PPE-0 : GUI CMD_EXECUTED : User nsroot - Remote_ip 10.55.1.100 - Command "login login tenant_name=Owner,password=***********,challenge_response=***********,token=1c81504d124245d,client_port=-1,cert_verified=false,sessionid=***********,session_timeout=900,permission=superuser" - Status "Done" # NOSONAR
def test_citrix_netscaler_sdx(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"test-ctitrixns-host-{uuid.uuid4().hex}"
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} svm_service: {{ host }}  {{ time }} GMT mynetscaler2 0-PPE-0 : GUI CMD_EXECUTED : User nsroot - Remote_ip 10.1.1.1 - Command "login login tenant_name=Owner,password=***********,challenge_response=***********,token=1c81504d124245d,client_port=-1,cert_verified=false,sessionid=***********,session_timeout=900,permission=superuser" - Status "Done"\n' # NOSONAR
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# [289]: AAA Message : In receive_ldap_user_search_event: ldap_first_entry returned null, user ssgconfig not found
def test_citrix_netscaler_sdx_AAA(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"test-ctitrixns-host-{uuid.uuid4().hex}"
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} [289]: AAA Message : In receive_ldap_user_search_event: ldap_first_entry returned null, user {{ host }} not found\n"
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw {{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <134> CEF:0|Citrix|NetScaler|NS13.0|APPFW|APPFW_JSON_DOS_MAX_OBJECT_KEY_LENGTH|6|src=131.105.71.188 spt=4149 method=GET request=http://10.160.0.10/test/file/jsonchecks.php msg=Object key at offset (1) exceeds maximum key length (3). cn1=112702 cn2=157553 cs1=test_profile cs2=PPE0 cs4=ERROR cs5=2021 act=blocked
def test_citrix_netscaler_appfw_cef(
    record_property,  setup_splunk, setup_sc4s
):
    mt = env.from_string(
        "{{ mark }} CEF:0|Citrix|NetScaler|NS13.0|APPFW|APPFW_JSON_DOS_MAX_OBJECT_KEY_LENGTH|6|src=131.105.71.188 spt=4149 method=GET request=http://10.160.0.10/test/file/jsonchecks.php msg=Object key at offset (1) exceeds maximum key length (3). cn1=112702 cn2=157553 cs1=test_profile cs2=PPE0 cs4=ERROR cs5=2021 act=blocked"
    )
    message = mt.render(mark="<134>")

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netfw sourcetype="citrix:netscaler:appfw:cef" earliest={epoch}'
    )
    search = st.render()

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <12> 01/11/2021:08:57:43 GMT Citrix 0-PPE-0 : default APPFW APPFW_STARTURL 5687021 0 :  10.160.44.137 392811-PPE0 - test_profile Disallow Illegal URL: http://10.160.0.10/0bef <not blocked>
def test_citrix_netscaler_appfw(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"test-ctitrixns-host-{uuid.uuid4().hex}"
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ time }} GMT {{ host }} 0-PPE-0 : default APPFW APPFW_STARTURL 5687021 0 :  10.160.44.137 392811-PPE0 - test_profile Disallow Illegal URL: http://10.160.0.10/0bef <not blocked>"
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:appfw"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    result_count, event_count = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
