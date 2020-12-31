# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
import random
from .timeutils import *

env = Environment()

# <12> 01/10/2001:01:01:01 GMT netscaler ABC-D : SSLVPN HTTPREQUEST 1234567 : Context username@192.0.2.1 - SessionId: 12345- example.com User username : Group(s) groupname : Vserver a1b2:c3d4:e5f6:a7b8:c9d0:e1f2:a3b4:c5d6:123 - 01/01/2001:01:01:01 GMT GET file/path.gif - -
def test_citrix_netscaler(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "test-ctitrixns-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ time }} {{ tzname }} {{ host }} ABC-D : SSLVPN HTTPREQUEST 1234567 : Context username@192.0.2.1 - SessionId: 12345- example.com User username : Group(s) groupname : Vserver a1b2:c3d4:e5f6:a7b8:c9d0:e1f2:a3b4:c5d6:123 - 01/01/2001:01:01:01 GMT GET file/path.gif - -\n"
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <134>Jun 18 18:18:42 svm_service: 1.1.1.1 18/06/2020:16:18:42 GMT : GUI CMD_EXECUTED : User nsroot - Remote_ip 10.55.1.100 - Command "login login tenant_name=Owner,password=***********,challenge_response=***********,token=1c81504d124245d,client_port=-1,cert_verified=false,sessionid=***********,session_timeout=900,permission=superuser" - Status "Done"
def test_citrix_netscaler_sdx(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "test-ctitrixns-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} svm_service: {{ host }} {{ time }} GMT : GUI CMD_EXECUTED : User nsroot - Remote_ip 10.1.1.1 - Command "login login tenant_name=Owner,password=***********,challenge_response=***********,token=1c81504d124245d,client_port=-1,cert_verified=false,sessionid=***********,session_timeout=900,permission=superuser" - Status "Done"\n'
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# [289]: AAA Message : In receive_ldap_user_search_event: ldap_first_entry returned null, user ssgconfig not found
def test_citrix_netscaler_sdx_AAA(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "test-ctitrixns-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Dec 31 15:20:45 22.255.14.163  12/31/2020:15:20:45 GMT mynetscaler1 0-PPE-0 : default EVENT STOPSYS 4326096 0 :  System stopped - Memory 1585RMB
def test_citrix_netscaler_vpx(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "test-ctitrixns-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    time = dt.strftime("%d/%m/%Y:%H:%M:%S")
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }}  {{ time }} GMT mynetscaler1 0-PPE-0 : default EVENT STOPSYS 4326096 0 :  System stopped - Memory 1585RMB\n"
    )
    message = mt.render(
        mark="<12>", bsd=bsd, time=time, tzname=tzname, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} sourcetype="citrix:netscaler:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
