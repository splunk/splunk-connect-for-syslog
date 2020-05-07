# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <134>Apr 14 10:42:05 xxxxx SymantecServer: Site: Site xxxxx,Server Name: xxxxx,Domain Name: Default,The management server received the client log successfully,yyyyyyy,zzzzzzzz,host.domain.suffix
def test_symantec_ep_agent(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} SymantecServer: Site: Site xxxxx,Server Name: xxxxx,Domain Name: Default,The management server received the client log successfully,yyyyyyy,zzzzzzzz,host.domain.suffix"
    )
    message = mt.render(mark="<134>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:agent:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:41:51 xxxxx-xxxxx SymantecServer: yyyyyy,Category: 2,LiveUpdate Manager,Event Description: A LiveUpdate session ran successfully.  No new updates were available.,Event time: 2020-04-14 10:41:33,Group Name: My Company\Default Group
def test_symantec_ep_agt_system(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: yyyyyy,Category: 2,LiveUpdate Manager,Event Description: A LiveUpdate session ran successfully.  No new updates were available.,Event time: 2020-04-14 10:41:33,Group Name: My Company\Default Group"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:agt:system:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 09:07:42 xxxxx-xxxxx SymantecServer: Site: Site xxxxx-xxxxx,Server Name: xxxxx-xxxxx,Event Description: No updates found for Application Control Data 14.2 RU2.
def test_symantec_ep_scm_system(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + "SymantecServer: Site: Site xxxxx-xxxxx,Server Name: xxxxx-xxxxx,Event Description: No updates found for Application Control Data 14.2 RU2."
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:scm:system:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:03:23 xxxxx-xxxxx SymantecServer: Scan ID: 1581582179,Begin: 2020-04-14 10:01:04,End Time: 2020-04-14 10:02:14,Completed,Duration (seconds): 70,User1: Spiderman,User2: Spiderman,Scan started on selected drives and folders and all extensions.,Scan Complete:  Risks: 0   Scanned: 1062   Files/Folders/Drives Omitted: 0 Trusted Files Skipped: 698,Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 1062,Omitted: 0,Computer: yyyyyyy,IP Address: 1.1.1.1,Domain Name: Default,Group Name: My Company\Preprod Tuesday,Server Name: xxxxx-xxxxx
def test_symantec_ep_scan(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: Scan ID: 1581582179,Begin: 2020-04-14 10:01:04,End Time: 2020-04-14 10:02:14,Completed,Duration (seconds): 70,User1: Spiderman,User2: Spiderman,Scan started on selected drives and folders and all extensions.,Scan Complete:  Risks: 0   Scanned: 1062   Files/Folders/Drives Omitted: 0 Trusted Files Skipped: 698,Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 1062,Omitted: 0,Computer: yyyyyyy,IP Address: 1.1.1.1,Domain Name: Default,Group Name: My Company\Preprod Tuesday,Server Name: xxxxx-xxxxx"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:scan:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:42:32 xxxxx-xxxxx SymantecServer: yyyyyy,...,Blocked,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,,Begin: 2020-04-14 10:36:40,End Time: 2020-04-14 10:36:40,Rule: ,3248,C:\PROGRAM FILES (X86)\BIGFIX ENTERPRISE\BES CLIENT\BESCLIENT.EXE,0,,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,User Name: SYSTEM,Domain Name: ,Action Type: 55,File size (bytes): ,Device ID: 
def test_symantec_ep_behavior(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: yyyyyy,...,Blocked,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,,Begin: 2020-04-14 10:36:40,End Time: 2020-04-14 10:36:40,Rule: ,3248,C:\PROGRAM FILES (X86)\BIGFIX ENTERPRISE\BES CLIENT\BESCLIENT.EXE,0,,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,User Name: SYSTEM,Domain Name: ,Action Type: 55,File size (bytes): ,Device ID: "
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:behavior:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
