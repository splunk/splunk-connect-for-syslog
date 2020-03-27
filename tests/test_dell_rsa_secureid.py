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

env = Environment()


# <14>Mar 25 15:09:33 {{ host }} 2020-03-25 15:09:33,503, {{ host }}.example.net, audit.admin.com.rsa.authmgr.internal.admin.principalmgt.impl.AMPrincipalAdministrationImpl, INFO,
# <11>Mar 25 15:04:54 {{ host }} 2020-03-25 15:04:54,485, {{ host }}.example.net, system.com.rsa.ims.configuration.impl.AuthorizationEnabledConfigurationServiceImpl, ERROR, xxxxx,xxxxx,10.0.0.1,10.0.0.1,CONF_READ,16153,FAIL,INSUFFICIENT_PRIVILEGE,xxxx-fnIz0FpnFNO0,xxxxx,xxx,xxx,xxxx,xxx,xxxx,0000-Global-0000,auth_manager.dashboard.hide.grpagent,,,,,
# <14>Mar 25 15:09:14 {{ host }} 2020-03-25 15:09:14,094, {{ host }}.example.net, audit.runtime.com.rsa.ims.authn.impl.AuthenticationBrokerImpl, INFO, xxxxx,xxxxx,10.0.0.1,10.0.0.1,AUTHN_LOGIN_EVENT,13002,SUCCESS,AUTHN_METHOD_SUCCESS,xxxx-Dnj467rNRh++,xxxx,xxx,xxxx,xxx,xxx,xxx,xxxx,946367dcb9f859941af8aee9b2462acc,10.0.0.1,hst-xxxxx.example.net,7,000000000000000000002000f1022000,SecurID_Native,,,AUTHN_LOGIN_EVENT,5,1,,,,,xxxxxxx,xxxxxxxx8632,,


testdata_admin = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, audit.admin.com.rsa.authmgr.internal.admin.principalmgt.impl.AMPrincipalAdministrationImpl, INFO,",
]
@pytest.mark.parametrize("event", testdata_admin)
def test_dell_rsa_secureid_admin(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:admin:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

testdata_system = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, system.com.rsa.ims.configuration.impl.AuthorizationEnabledConfigurationServiceImpl, ERROR, xxxxx,xxxxx,10.0.0.1,10.0.0.1,CONF_READ,16153,FAIL,INSUFFICIENT_PRIVILEGE,xxxx-fnIz0FpnFNO0,xxxxx,xxx,xxx,xxxx,xxx,xxxx,0000-Global-0000,auth_manager.dashboard.hide.grpagent,,,,,",
]
@pytest.mark.parametrize("event", testdata_system)
def test_dell_rsa_secureid_system(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:system:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

testdata_runtime = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, audit.runtime.com.rsa.ims.authn.impl.AuthenticationBrokerImpl, INFO, xxxxx,xxxxx,10.0.0.1,10.0.0.1,AUTHN_LOGIN_EVENT,13002,SUCCESS,AUTHN_METHOD_SUCCESS,xxxx-Dnj467rNRh++,xxxx,xxx,xxxx,xxx,xxx,xxx,xxxx,946367dcb9f859941af8aee9b2462acc,10.0.0.1,hst-xxxxx.example.net,7,000000000000000000002000f1022000,SecurID_Native,,,AUTHN_LOGIN_EVENT,5,1,,,,,xxxxxxx,xxxxxxxx8632,,",
]
@pytest.mark.parametrize("event", testdata_runtime)
def test_dell_rsa_secureid_runtime(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:runtime:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_dell_rsa_secureid_trace(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "test_rsasecureid-" + get_host_key

    events = [
        '{{ mark }}{{ bsd }} {{ host }} Caused by: org.postgresql.util.PSQLException: The column index is out of range: 3, number of columns: 2.',
        '{{ mark }}{{ bsd }} {{ host }}     at org.springframework.transaction.support.TransactionTemplate.execute(TransactionTemplate.java:131)',
        '{{ mark }}{{ bsd }} {{ host }}     at sun.reflect.GeneratedMethodAccessor250.invoke(Unknown Source)',
        '{{ mark }}{{ bsd }} {{ host }}     at weblogic.rmi.internal.wls.WLSExecuteRequest.run(WLSExecuteRequest.java:138)',
        '{{ mark }}{{ bsd }} {{ host }}     at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)',
        '{{ mark }}{{ bsd }} {{ host }}     at com.rsa.command.CommandServerEjb30_vraifm_CommandServerEjb30Impl.__WL_invoke(Unknown Source)',
        '{{ mark }}{{ bsd }} {{ host }}     at org.postgresql.core.v3.SimpleParameterList.setStringParameter(SimpleParameterList.java:118)',
        '{{ mark }}{{ bsd }} {{ host }} Caused by: org.postgresql.util.PSQLException: The column index is out of range: 3, number of columns: 2.',
        '{{ mark }}{{ bsd }} {{ host }}     at weblogic.work.ExecuteThread.execute(ExecuteThread.java:420)',
        '{{ mark }}{{ bsd }} {{ host }}     at com.rsa.security.SecurityContext.doAs(SecurityContext.java:439)',
        '{{ mark }}{{ bsd }} {{ host }}     at com.bea.core.repackaged.springframework.aop.support.DelegatingIntroductionInterceptor.doProceed(DelegatingIntroductionInterceptor.java:133)',
        '{{ mark }}{{ bsd }} {{ host }}     at weblogic.work.SelfTuningWorkManagerImpl.runWorkUnderContext(SelfTuningWorkManagerImpl.java:652)',
        '{{ mark }}{{ bsd }} {{ host }}     at com.rsa.ims.command.LocalTransactionalCommandTarget$2.doInTransaction(LocalTransactionalCommandTarget.java:1)',
        '{{ mark }}{{ bsd }} {{ host }}     at org.jboss.weld.ejb.SessionBeanInterceptor.aroundInvoke(SessionBeanInterceptor.java:52)',
        '{{ mark }}{{ bsd }} {{ host }}     at weblogic.rmi.internal.BasicServerRef.handleRequest(BasicServerRef.java:531)',
        '{{ mark }}{{ bsd }} {{ host }}     at com.rsa.command.CommandServerEngine$CommandExecutor.run(CommandServerEngine.java:933)',
    ]
    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")

    # Tune time functions
    epoch = epoch[:-7]
    for event in events:
        mt = env.from_string(event + "\n")
        message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)
        sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:trace" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount >0