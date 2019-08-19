# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from flaky import flaky
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


@flaky(max_runs=3, min_passes=2)
#<134> Jan 29 01:38:50 192.168.1.1 SymantecServer: PIPO-SRV: Scan ID: 1296264604,Begin: 2011-01-29 01:29:50,End: 2011-01-29,Completed,Duration (seconds): 98,User1: SYSTEM,User2: SYSTEM,"Scan started on selected drives and folders and all extensions.","Scan Complete:  Risks: 0   Scanned: 891   Files/Folders/Drives Omitted: 0",Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 891,Omitted: 0,Computer: MyServer15,IP Address: 192.168.1.1,Domain: MyDomain,Group: My Company\MyDomain_DC\Virtual Servers,Server: PIPO-SRV
def test_symantec_ep_syslog_syslogscan(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: PIPO-SRV: Scan ID: 1296264604,Begin: 2011-01-29 01:29:50,End: 2011-01-29,Completed,Duration (seconds): 98,User1: SYSTEM,User2: SYSTEM,'Scan started on selected drives and folders and all extensions.','Scan Complete:  Risks: 0   Scanned: 891   Files/Folders/Drives Omitted: 0',Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 891,Omitted: 0,Computer: MyServer15,IP Address: 192.168.1.1,Domain: MyDomain,Group: My Company\MyDomain_DC\Virtual Servers,Server: PIPO-SRV")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:scan:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@flaky(max_runs=3, min_passes=2)
#<134> Jan 28 13:20:54 192.168.1.1 SymantecServer PIPO-SRV: Site: PIPO-SRV,Server: PIPO-SRV,Domain: MyDomain,Admin: admin,Policy has been edited,TestServers policy LiveUpdate
def test_symantec_ep_syslog_admin(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r"{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: Site: My Site,Server: WIN-SQ91TVP2E4T,Domain: Default,Admin: admin,Administrator log on succeeded")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:admin:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@flaky(max_runs=3, min_passes=2)
#Apr 17 16:52:35 zusnwi08 SymantecServer AI183037,SHA-256: ,MD-5: ,Local: 239.255.255.250,Local: 1900,Local: 01005E7FFFFA,Remote: 192.168.64.2,Remote: ,Remote: 62461,Remote: 28D24492A977,UDP,Inbound,Begin: 2018-04-17 15:13:55,End: 2018-04-17 15:13:55,Occurrences: 1,Application: ,Rule: Allow UPnP Discovery from private IP addresses,Location: Inside the UTC Network,User: gopinap,Domain: CORP,Action: Allowed
def test_symantec_ep_syslog_traffic(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer AI183037,SHA-256: ,MD-5: ,Local: 239.255.255.250,Local: 1900,Local: 01005E7FFFFA,Remote: 192.168.64.2,Remote: ,Remote: 62461,Remote: 28D24492A977,UDP,Inbound,Begin: 2018-04-17 15:13:55,End: 2018-04-17 15:13:55,Occurrences: 1,Application: ,Rule: Allow UPnP Discovery from private IP addresses,Location: Inside the UTC Network,User: gopinap,Domain: CORP,Action: Allowed")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:traffic:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1



@flaky(max_runs=3, min_passes=2)
#<134> Jan 30 22:07:50 192.168.1.1 SymantecServer PIPO-SRV: Site: PIPO-SRV,Server: PIPO-SRV,LUALL.EXE has been launched.
def test_symantec_ep_syslog_syslogscm_system(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: Site: My Site,Server: WIN-SQ91TVP2E4T,Symantec Endpoint Protection Manager server started with trial license.")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)
    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:scm_system:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk,search)
    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
@flaky(max_runs=3, min_passes=2)
#<134> Jan 28 13:24:39 192.168.1.1 SymantecServer PIPO-SRV: server11,Category: 0,Smc,Connected to Symantec Endpoint Protection Manager (192.168.1.1)
def test_symantec_ep_syslog_syslogagt_system(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer:  WIN-SQ91TVP2E4T,Category: 2,LiveUpdate Manager,An update for Revocation Data from LiveUpdate was successfully installed.  The new sequence number is 190730025.    Content was downloaded from HTTPS://liveupdate.symantecliveupdate.com/ (443).,Event time: 2019-07-30 11:25:05")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)
    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:agt_system:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk,search)
    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)
    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
#<134> Jan 28 13:24:39 192.168.1.1 SymantecServer PIPO-SRV: server11,Category: 0,Smc,Connected to Symantec Endpoint Protection Manager (192.168.1.1)
def test_symantec_ep_syslog_syslogagt_behavior(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: WIN-SQ91TVP2E4T,10.0.2.15,Continue,Application and Device Control is ready,System,Begin: 2019-07-30 11:26:07,End: 2019-07-30 11:26:07,Rule: Built-in rule,0,SysPlant,0,SysPlant,None,User: None,Domain: WORKGROUP,Action Type: ,File size (bytes): 0,Device ID: 98")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)
    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:behavior:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk,search)
    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
@flaky(max_runs=3, min_passes=2)
def test_symantec_ep_syslog_syslogagt_proactive(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        r"{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: Computer name: WIN-SQ91TVP2E4T,Source: Auto-Protect scan,Risk name: EICAR Test String,Occurrences: 1,C:\Users\Administrator\Downloads\eicar.com,,Actual action: Cleaned by deletion,Requested action: Cleaned,Secondary action: Quarantined,Event time: 2019-08-05 14:40:10,Inserted: 2019-08-05 14:41:27,End: 2019-08-05 14:40:10,Last update time: 2019-08-05 14:41:27,Domain: Default,Group: My Company\Default Group,Server: WIN-SQ91TVP2E4T,User: Administrator,Source computer: ,Source IP: ,Disposition: Bad,Risk action: Deleted,Download site: ,Web domain: ,Downloaded by: chrome.exe,Prevalence: This file has been seen by hundreds of thousands of Symantec users.,Confidence: This file is untrustworthy.,URL Tracking Status: On,First Seen: Symantec has known about this file for more than 1 year.,Sensitivity: ,Not on the permitted application list,Application hash: ,Hash type: SHA2,Company name: ,Application name: ,Application version: ,Application type: 127,File size (bytes): 68,Category set: Malware,Category type: Virus,Location: Default,Intensive Protection Level: 0,Certificate issuer: ,Certificate signer: ,Certificate thumbprint: ,Signing timestamp: 0,Certificate serial number:")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)
    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:proactive:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk,search)
    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
#<134> Jan 28 13:24:39 192.168.1.1 SymantecServer PIPO-SRV: server11,Category: 0,Smc,Connected to Symantec Endpoint Protection Manager (192.168.1.1)
def test_symantec_ep_syslog_syslogagt_risk(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    mt = env.from_string(
        r"{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }}  SymantecServer: Deleted,IP Address: 10.0.2.4,Computer name: WIN-SQ91TVP2E4T,Intensive Protection Level: , Certificate issuer: , Certificate signer: ,Certificate thumbprint: ,Signing timestamp: ,Certificate serial number: ,Source: Auto-Protect scan,Risk name: EICAR Test String,Occurrences: 1,C:\Users\Administrator\Downloads\eicar.com,none,Actual action: Cleaned by deletion,Requested action: Cleaned,Secondary action: Quarantined,Event time: 2019-08-05 14:40:10,Inserted: 2019-08-05 14:41:27,End: 2019-08-05 14:40:10,Last update time: 2019-08-05 14:41:27,Domain: Default,Group: My Company\Default Group,Server: WIN-SQ91TVP2E4T,User: Administrator,Source computer: ,Source IP: ,Disposition: Bad,Download site: ,Web domain: ,Downloaded by: chrome.exe,Prevalence: This file has been seen by hundreds of thousands of Symantec users.,Confidence: This file is untrustworthy.,URL Tracking Status: On,First Seen: Symantec has known about this file for more than 1 year.,Sensitivity: ,Not on the permitted application list,Application hash: ,Hash type: SHA2,Company name: ,Application name: ,Application version: ,Application type: 127,File size (bytes): 68,Category set: Malware,Category type: Virus,Location: Default")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:risk:file\" | head 2")
    search = st.render(host=host)
    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

@flaky(max_runs=3, min_passes=2)
#<134> Jan 29 01:38:50 192.168.1.1 SymantecServer: PIPO-SRV: Scan ID: 1296264604,Begin: 2011-01-29 01:29:50,End: 2011-01-29,Completed,Duration (seconds): 98,User1: SYSTEM,User2: SYSTEM,"Scan started on selected drives and folders and all extensions.","Scan Complete:  Risks: 0   Scanned: 891   Files/Folders/Drives Omitted: 0",Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 891,Omitted: 0,Computer: MyServer15,IP Address: 192.168.1.1,Domain: MyDomain,Group: My Company\MyDomain_DC\Virtual Servers,Server: PIPO-SRV
def test_symantec_ep_syslog_syslogpolicy(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer: Site: My Site,Server: WIN-SQ91TVP2E4T,Domain: Default,Admin: admin,Added shared policy upon system install: Added shared policy upon system install,Integrations policy")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:policy:file\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


@flaky(max_runs=3, min_passes=2)
#<134> Jan 28 13:24:39 192.168.1.1 SymantecServer PIPO-SRV: server11,Category: 0,Smc,Connected to Symantec Endpoint Protection Manager (192.168.1.1)
def test_symantec_ep_syslog_syslogagent(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} SymantecServer PIPO-SRV: Site: My Site,Server: WIN-SQ91TVP2E4T,Domain: Default,The client has downloaded globalindex.dax,WIN-SQ91TVP2E4T,Administrator,LocalComputer")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"symantec:ep:agent:file\" | head 2")
    search = st.render(host=host)
    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
