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


# <14>Mar 25 15:09:33 {{ host }} 2020-03-25 15:09:33,503, {{ host }}.example.net, audit.admin.com.rsa.authmgr.internal.admin.principalmgt.impl.AMPrincipalAdministrationImpl, INFO,
# <11>Mar 25 15:04:54 {{ host }} 2020-03-25 15:04:54,485, {{ host }}.example.net, system.com.rsa.ims.configuration.impl.AuthorizationEnabledConfigurationServiceImpl, ERROR, xxxxx,xxxxx,10.0.0.1,10.0.0.1,CONF_READ,16153,FAIL,INSUFFICIENT_PRIVILEGE,xxxx-fnIz0FpnFNO0,xxxxx,xxx,xxx,xxxx,xxx,xxxx,0000-Global-0000,auth_manager.dashboard.hide.grpagent,,,,,
# <14>Mar 25 15:09:14 {{ host }} 2020-03-25 15:09:14,094, {{ host }}.example.net, audit.runtime.com.rsa.ims.authn.impl.AuthenticationBrokerImpl, INFO, xxxxx,xxxxx,10.0.0.1,10.0.0.1,AUTHN_LOGIN_EVENT,13002,SUCCESS,AUTHN_METHOD_SUCCESS,xxxx-Dnj467rNRh++,xxxx,xxx,xxxx,xxx,xxx,xxx,xxxx,946367dcb9f859941af8aee9b2462acc,10.0.0.1,hst-xxxxx.example.net,7,000000000000000000002000f1022000,SecurID_Native,,,AUTHN_LOGIN_EVENT,5,1,,,,,xxxxxxx,xxxxxxxx8632,,


testdata_admin = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, audit.admin.com.rsa.authmgr.internal.admin.principalmgt.impl.AMPrincipalAdministrationImpl, INFO,",
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.rsatest.local, audit.admin.authmgr.FileDataAdministration, INFO, 9ce24a09339aa00a3325c4e6e7ef2f7e,1661df9a339aa00a7e70bd39a51aa886,x.x.x.x,x.x.x.x,AUTHMGR_FILE_CREATE,20081,SUCCESS,,xxxxxxxx339aa00a17ab4744de7xxxxx-E57wD7+hB6H1,,00000000000000000000100xxxxxxxxx,xxxxxxxxxx00000000001000d0011000,000000000000000000001000exxxxxxx,xxxxxx,Admin,Admin,AM_FILE,,,0000000000000000000xxxxxxxx,node_secret.zip,,,,,,",
]


@pytest.mark.parametrize("event", testdata_admin)
@pytest.mark.addons("dell")
def test_dell_rsa_secureid_admin(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")[:-3]

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:admin:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_system = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, system.com.rsa.ims.configuration.impl.AuthorizationEnabledConfigurationServiceImpl, ERROR, xxxxx,xxxxx,10.0.0.1,10.0.0.1,CONF_READ,16153,FAIL,INSUFFICIENT_PRIVILEGE,xxxx-fnIz0FpnFNO0,xxxxx,xxx,xxx,xxxx,xxx,xxxx,0000-Global-0000,auth_manager.dashboard.hide.grpagent,,,,,",
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}, system..backup.scheduler.service.AsyncBackupJobWorkerImpl, INFO, xxxxxxxxxx00a5d7449d0a52c9041,xxxxxxxxxx0a7e70bd39a51aa886,x.x.x.x,x.x.x.x,OC_SCHEDULE_CREATE_BACKUP,26164,SUCCESS,,,,,,SYSTEM,,,2022061xx.RSAbackup,,,,,,", 
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }},system.ionsconsole.admin.backuprestore.BackupFilesManager,INFO,0714e153339aa00a7abfa7d5d7a1b155,xxxxxxxxxx9aa00a7e70bd39a51aa886,x.x.x.x,x.x.x.x,DELETE_AGED_BACKUP,26161,SUCCESS,,,,,,SYSTEM,,,/opt/rsa/am/backup/202205xxxxxxxxxx.RSAbackup,,,,,,",
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}, system.b.operationsconsole.action.ManageReplicationAction, INFO, xxxxxxxxxx339aa00a7d39e7bab4059d84,xxxxxxxxxx9aa00a7e70bd39axxxxxxxxxx,x.x.x.x,x.x.x.x,OC_REPLICATION_STATUS,16280,SUCCESS,,,,,,xxxxxxxxxx,,,,,,,,,",
]


@pytest.mark.parametrize("event", testdata_system)
@pytest.mark.addons("dell")
def test_dell_rsa_secureid_system(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")[:-3]

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:system:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


testdata_runtime = [
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}.example.net, audit.runtime.com.rsa.ims.authn.impl.AuthenticationBrokerImpl, INFO, xxxxx,xxxxx,10.0.0.1,10.0.0.1,AUTHN_LOGIN_EVENT,13002,SUCCESS,AUTHN_METHOD_SUCCESS,xxxx-Dnj467rNRh++,xxxx,xxx,xxxx,xxx,xxx,xxx,xxxx,946367dcb9f859941af8aee9b2462acc,10.0.0.1,hst-xxxxx.example.net,7,000000000000000000002000f1022000,SecurID_Native,,,AUTHN_LOGIN_EVENT,5,1,,,,,xxxxxxx,xxxxxxxx8632,,",
    "{{ mark }}{{ bsd }} {{ host }} {{ date }} {{ rsatime }}, {{ host }}, audit.runtime.sa.ims.web.operationsconsole.action.SecurityAction, INFO, 6a4e6d23339aa00a4d0fe99413705d2d,1661df9a339aa00a7e70bd39a51aa886,x.x.x.x,x.x.x.x,OC_ADMIN_LOGIN_EVENT,13006,SUCCESS,,,,,,xxxxxxx,,,,,,,0,,,,,,,,,,,,,,,",
]


@pytest.mark.parametrize("event", testdata_runtime)
@pytest.mark.addons("dell")
def test_dell_rsa_secureid_runtime(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = "test_rsasecureid-" + get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)
    rsatime = dt.strftime("%H:%M:%S,%f")[:-3]

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host, date=date, rsatime=rsatime)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:runtime:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("dell")
def test_dell_rsa_secureid_trace(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = "test_rsasecureid-" + get_host_key

    events = [
        "{{ mark }}{{ bsd }} {{ host }} Caused by: org.postgresql.util.PSQLException: The column index is out of range: 3, number of columns: 2.",
        "{{ mark }}{{ bsd }} {{ host }}     at org.springframework.transaction.support.TransactionTemplate.execute(TransactionTemplate.java:131)",
        "{{ mark }}{{ bsd }} {{ host }}     at sun.reflect.GeneratedMethodAccessor250.invoke(Unknown Source)",
        "{{ mark }}{{ bsd }} {{ host }}     at weblogic.rmi.internal.wls.WLSExecuteRequest.run(WLSExecuteRequest.java:138)",
        "{{ mark }}{{ bsd }} {{ host }}     at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)",
        "{{ mark }}{{ bsd }} {{ host }}     at com.rsa.command.CommandServerEjb30_vraifm_CommandServerEjb30Impl.__WL_invoke(Unknown Source)",
        "{{ mark }}{{ bsd }} {{ host }}     at org.postgresql.core.v3.SimpleParameterList.setStringParameter(SimpleParameterList.java:118)",
        "{{ mark }}{{ bsd }} {{ host }} Caused by: org.postgresql.util.PSQLException: The column index is out of range: 3, number of columns: 2.",
        "{{ mark }}{{ bsd }} {{ host }}     at weblogic.work.ExecuteThread.execute(ExecuteThread.java:420)",
        "{{ mark }}{{ bsd }} {{ host }}     at com.rsa.security.SecurityContext.doAs(SecurityContext.java:439)",
        "{{ mark }}{{ bsd }} {{ host }}     at com.bea.core.repackaged.springframework.aop.support.DelegatingIntroductionInterceptor.doProceed(DelegatingIntroductionInterceptor.java:133)",
        "{{ mark }}{{ bsd }} {{ host }}     at weblogic.work.SelfTuningWorkManagerImpl.runWorkUnderContext(SelfTuningWorkManagerImpl.java:652)",
        "{{ mark }}{{ bsd }} {{ host }}     at com.rsa.ims.command.LocalTransactionalCommandTarget$2.doInTransaction(LocalTransactionalCommandTarget.java:1)",
        "{{ mark }}{{ bsd }} {{ host }}     at org.jboss.weld.ejb.SessionBeanInterceptor.aroundInvoke(SessionBeanInterceptor.java:52)",
        "{{ mark }}{{ bsd }} {{ host }}     at weblogic.rmi.internal.BasicServerRef.handleRequest(BasicServerRef.java:531)",
        "{{ mark }}{{ bsd }} {{ host }}     at com.rsa.command.CommandServerEngine$CommandExecutor.run(CommandServerEngine.java:933)",
    ]
    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]
    for event in events:
        mt = env.from_string(event + "\n")
        message = mt.render(mark="<166>", bsd=bsd, host=host, date=date)
        sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netauth _time={{ epoch }} sourcetype="rsa:securid:trace" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count > 0
