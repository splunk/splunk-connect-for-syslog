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

# Apr 14 10:10:10 dummyhost SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,Event Description: Administrator log on failed
def test_symantec_ep_admin(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,Event Description: Administrator log on failed"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:admin:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: ccccc,Local Host IP: 10.0.8.1,Local Port: 50221,Remote Host IP: 10.0.1.2,Remote Host Name: qqqqq,Remote Port: 20362,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed
def test_symantec_ep_packet(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: ccccc,Local Host IP: 10.0.8.1,Local Port: 50221,Remote Host IP: 10.0.1.2,Remote Host Name: qqqqq,Remote Port: 20362,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:packet:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,"Event Description: Policy has been edited: Changed Console mode at [Default]",Client Policy
def test_symantec_ep_policy(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r'SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,"Event Description: Policy has been edited: Changed Console mode at [Default]",Client Policy'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:policy:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: Potential risk found,Computer name: ooooo,IP Address: 10.0.0.2,Detection type: System Change HostFile,First Seen: Symantec has known about this file for more than 1 year.,Application name: Microsoft\xAE Windows\xAE Operating System,Application type: 127,Application version: 6.1.7600.16385,Hash type: SHA-256,Application hash: ded6fc40-4365-4ba0-8446-3fa77a30cb6e,Company name: KKK.,LLLL,MMMM,File size (bytes): 3507,Sensitivity: 2,Detection score: 3,COH Engine Version: ,Detection Submissions No,Permitted application reason: Not on the permitted application list,Disposition: Bad,Download site: http://attraction.example.org/,Web domain: tkhwesmptszdody.dm,Downloaded by: c:/users/administrator/desktop/tools/tools/xxxtools.exe,Prevalence: Unknown,Confidence: There is not enough information about this file to recommend it.,URL Tracking Status: on,Risk Level: High,Risk type: 3,Source: Heuristic Scan,Risk name: Trojan.Gen.2,Occurrences: 9,PolicyZZZ,Realtime deferred scanning,Actual action: Left alone,Requested action: Quarantined,Secondary action: Left alone,Event time: 2020-05-04 06:57:02,Inserted: 2020-05-04 06:57:02,End: 2020-05-04 06:57:02,Domain: Domain A,Group: My Company\Default Group,Server: Example Server C,User: user_b,Source computer: fffff,Source IP: 10.0.9.2,Intensive Protection Level: 0,Certificate issuer: Symantec,Certificate signer: Unizeto,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 149843929435818692848040365716851702463
def test_symantec_ep_proactive(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: Potential risk found,Computer name: ooooo,IP Address: 10.0.0.2,Detection type: System Change HostFile,First Seen: Symantec has known about this file for more than 1 year.,Application name: Microsoft\xAE Windows\xAE Operating System,Application type: 127,Application version: 6.1.7600.16385,Hash type: SHA-256,Application hash: ded6fc40-4365-4ba0-8446-3fa77a30cb6e,Company name: KKK.,LLLL,MMMM,File size (bytes): 3507,Sensitivity: 2,Detection score: 3,COH Engine Version: ,Detection Submissions No,Permitted application reason: Not on the permitted application list,Disposition: Bad,Download site: http://attraction.example.org/,Web domain: tkhwesmptszdody.dm,Downloaded by: c:/users/administrator/desktop/tools/tools/xxxtools.exe,Prevalence: Unknown,Confidence: There is not enough information about this file to recommend it.,URL Tracking Status: on,Risk Level: High,Risk type: 3,Source: Heuristic Scan,Risk name: Trojan.Gen.2,Occurrences: 9,PolicyZZZ,Realtime deferred scanning,Actual action: Left alone,Requested action: Quarantined,Secondary action: Left alone,Event time: 2020-05-04 06:57:02,Inserted: 2020-05-04 06:57:02,End: 2020-05-04 06:57:02,Domain: Domain A,Group: My Company\Default Group,Server: Example Server C,User: user_b,Source computer: fffff,Source IP: 10.0.9.2,Intensive Protection Level: 0,Certificate issuer: Symantec,Certificate signer: Unizeto,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 149843929435818692848040365716851702463"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:proactive:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: qqqqq,Event Description: "Web Attack: Fake Scan Webpage 7",Local Host IP: 10.0.3.4,Local Host MAC: c1411f5F9502,Remote Host Name: eeeee,Remote Host IP: 10.0.3.6,Remote Host MAC: aD31CCFD3eFF,Inbound,TCP,Intrusion ID: 1,Begin: 2020-05-06 09:06:09,End Time: 2020-05-06 09:06:09,Occurrences: 3,Application: C:/Windows/System32/example_x.exe,Location: Internal,User Name: user_h,Domain Name: CompanyXX,Local Port: 1991,Remote Port: 46926,CIDS Signature ID: 25198,CIDS Signature string: Web Attack: Fake Scan Webpage 7,CIDS Signature SubID: 25378,Intrusion URL: https://www.example.org/,Intrusion Payload URL: http://www.example.com/,SHA-256: 6d2fe32dc4249ef7e7359c6d874fffbbf335e832e49a2681236e1b686af78794,MD-5: 70270ca63a3de2d8905a9181a0245e58
def test_symantec_ep_security(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r'SymantecServer: qqqqq,Event Description: "Web Attack: Fake Scan Webpage 7",Local Host IP: 10.0.3.4,Local Host MAC: c1411f5F9502,Remote Host Name: eeeee,Remote Host IP: 10.0.3.6,Remote Host MAC: aD31CCFD3eFF,Inbound,TCP,Intrusion ID: 1,Begin: 2020-05-06 09:06:09,End Time: 2020-05-06 09:06:09,Occurrences: 3,Application: C:/Windows/System32/example_x.exe,Location: Internal,User Name: user_h,Domain Name: CompanyXX,Local Port: 1991,Remote Port: 46926,CIDS Signature ID: 25198,CIDS Signature string: Web Attack: Fake Scan Webpage 7,CIDS Signature SubID: 25378,Intrusion URL: https://www.example.org/,Intrusion Payload URL: http://www.example.com/,SHA-256: 6d2fe32dc4249ef7e7359c6d874fffbbf335e832e49a2681236e1b686af78794,MD-5: 70270ca63a3de2d8905a9181a0245e58'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:security:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: Security risk found,IP Address: 10.0.3.1,Computer name: qqqqq,Source: Definition downloader,Risk name: Backdoor.Joggver,Occurrences: 7,e:\resharper 9.1 + keygen\resharper.8.x.keygen.exe,"Still contains, 2 infected items",Actual action: Quarantined,Requested action: Process terminate pending restartLeft alone,Secondary action: Quarantined,Event time: 2020-05-06 08:29:27,Inserted: 2020-05-06 08:29:27,End: 2020-05-06 08:29:27,Last update time: 2020-05-06 08:29:27,Domain: SomeComp,Group: My Company\\Default Group,Server: Example Server C,User: user_h,Source computer: hhhhh,Source IP: 10.0.4.1,Disposition: Reputation was not used in this detection.,Download site: http://bbbb.example.com/,Web domain: gqtavlakkdkcryl.xn--pgbs0dh,Downloaded by: c:/program files (x86)/ggggg/cccc/application/cccc.exe,Prevalence: This file has been seen by fewer than 100 Symantec users.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: low,MDS,Application hash: 44d7fb7e-8c40-4a17-9aff-9c4aa0b96696,Hash type: SHA1,Company name: "Sample Inc. a wholly owned subsidiary of Dummy, Inc.",Application name: Setup Factory 7.0 Runtime,Application version: ,Application type: 127,File size (bytes): 1318,Category set: Security risk,Category type: UNKNOWN,Location: AZ - Office,Intensive Protection Level: 0,Certificate issuer: "Realtime deferred scanning",Certificate signer: Comodo,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 903804111
def test_symantec_ep_risk(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r'SymantecServer: Security risk found,IP Address: 10.0.3.1,Computer name: qqqqq,Source: Definition downloader,Risk name: Backdoor.Joggver,Occurrences: 7,e:\resharper 9.1 + keygen\resharper.8.x.keygen.exe,"Still contains, 2 infected items",Actual action: Quarantined,Requested action: Process terminate pending restartLeft alone,Secondary action: Quarantined,Event time: 2020-05-06 08:29:27,Inserted: 2020-05-06 08:29:27,End: 2020-05-06 08:29:27,Last update time: 2020-05-06 08:29:27,Domain: SomeComp,Group: My Company\\Default Group,Server: Example Server C,User: user_h,Source computer: hhhhh,Source IP: 10.0.4.1,Disposition: Reputation was not used in this detection.,Download site: http://bbbb.example.com/,Web domain: gqtavlakkdkcryl.xn--pgbs0dh,Downloaded by: c:/program files (x86)/ggggg/cccc/application/cccc.exe,Prevalence: This file has been seen by fewer than 100 Symantec users.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: low,MDS,Application hash: 44d7fb7e-8c40-4a17-9aff-9c4aa0b96696,Hash type: SHA1,Company name: "Sample Inc. a wholly owned subsidiary of Dummy, Inc.",Application name: Setup Factory 7.0 Runtime,Application version: ,Application type: 127,File size (bytes): 1318,Category set: Security risk,Category type: UNKNOWN,Location: AZ - Office,Intensive Protection Level: 0,Certificate issuer: "Realtime deferred scanning",Certificate signer: Comodo,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 903804111'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:risk:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Apr 14 10:10:10 dummyhost SymantecServer: nnnnn,Local Host IP: 10.0.0.2,Local Port: 10456,Local Host MAC: B9e90F5c3aC4,Remote Host IP: 10.0.9.2,Remote Host Name: lllll,Remote Port: 58999,Remote Host MAC: 7b6A329f7c1e,others,Inbound,Begin: 2020-05-06 09:18:32,End: 2020-05-06 09:18:32,Occurrences: 8,Application: C:/Windows/System32/example_y.EXE,Rule: Block all other IP traffic and log,Location: Public Network,User: user_f,Domain: XXXXDOMAIN,Action: Blocked,SHA-256: d1616b874a96df2515da372a90bddc00792cbff027f5e097cafa31d3aea8b310,MD-5: 82136b4240d6ce4ea7d03e51469a393b
def test_symantec_ep_traffic(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} " + r"SymantecServer: nnnnn,Local Host IP: 10.0.0.2,Local Port: 10456,Local Host MAC: B9e90F5c3aC4,Remote Host IP: 10.0.9.2,Remote Host Name: lllll,Remote Port: 58999,Remote Host MAC: 7b6A329f7c1e,others,Inbound,Begin: 2020-05-06 09:18:32,End: 2020-05-06 09:18:32,Occurrences: 8,Application: C:/Windows/System32/example_y.EXE,Rule: Block all other IP traffic and log,Location: Public Network,User: user_f,Domain: XXXXDOMAIN,Action: Blocked,SHA-256: d1616b874a96df2515da372a90bddc00792cbff027f5e097cafa31d3aea8b310,MD-5: 82136b4240d6ce4ea7d03e51469a393b"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:traffic:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:42:05 SymantecServer: xxx,Site: Site TUPI-PDSCCM01,Server Name: C1560245824,Domain Name: Default,The management server received the client log successfully,D1560245728,user226,local
def test_symantec_ep_agent_v14_3_33(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{host}},Site: Site TUPI-PDSCCM01,Server Name: C1560245824,Domain Name: Default,The management server received the client log successfully,D1560245728,user226,local"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
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

<50>Apr 14 10:41:51 SymantecServer: xxx,D1560245728,Category: 0,Symantec Endpoint Protection,Event Description: Symantec Endpoint Protection services startup was successful.,Event time: 2021-03-10 11:14:39,Group Name: My Company\Prod No Liveupdate
def test_symantec_ep_agt_system_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{host}},D1560245728,Category: 0,Symantec Endpoint Protection,Event Description: Symantec Endpoint Protection services startup was successful.,Event time: 2021-03-10 11:14:39,Group Name: My Company\Prod No Liveupdate"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
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

# <50>Apr 14 09:07:42 SymantecServer: xxx,Site: Site_D,Server Name: C1560245824,Event Description: Symantec Endpoint Protection Manager server started with paid license.
def test_symantec_ep_scm_system_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{host}},Site: Site_D,Server Name: C1560245824,Event Description: Symantec Endpoint Protection Manager server started with paid license."
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
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

# <50>Apr 14 10:03:23 SymantecServer: xxx,Scan ID: 1429255498,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Started,Duration (seconds): 91237,User1: user196,User2: user202,'Scan started on selected drives and folders and all extensions.','Scan stopped',Command: Not a command scan (),Threats: 10,Infected: 3,Total files: 454448,Omitted: 481,Computer: dest-sample_host66,IP Address: 127.0.0.1,Domain Name: XXComp,Group Name: My Company\Products,Server Name: C1560245824,Scan Type: ScanNow_Full
def test_symantec_ep_scan_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},Scan ID: 1429255498,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Started,Duration (seconds): 91237,User1: user196,User2: user202,'Scan started on selected drives and folders and all extensions.','Scan stopped',Command: Not a command scan (),Threats: 10,Infected: 3,Total files: 454448,Omitted: 481,Computer: dest-sample_host66,IP Address:127.0.0.1,Domain Name: XXComp,Group Name: My Company\Products,Server Name: C1560245824,Scan Type: ScanNow_Full"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
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

# <50>Apr 14 10:42:32 SymantecServer: xxx,D1560245728,127.0.0.1,Continue,AC9-1.1 Block access to autorun.inf - Caller MD5=xxxxxxb1435662fc6c672e25beb37be3,File Read,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Rule: All Applications Autorun.inf,4863,C:\PROGRAM FILES (X86)\sssssss ANTI-MALWARE\zzzzzz.EXE,0,No Module Name,E:/autorun.inf,User Name: user156,Domain Name: CompanyZ,Action Type: ,File size (bytes): 4402,Device ID: USBSTOR\Disk&Ven_TOSHIBA&Prod_External_USB_3.0&REV_9020141571855308750352033
def test_symantec_ep_behavior_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},D1560245728,127.0.0.1,Continue,AC9-1.1 Block access to autorun.inf - Caller MD5=xxxxxxb1435662fc6c672e25beb37be3,File Read,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Rule: All Applications Autorun.inf,4863,C:\PROGRAM FILES (X86)\sssssss ANTI-MALWARE\zzzzzz.EXE,0,No Module Name,E:/autorun.inf,User Name: user156,Domain Name: CompanyZ,Action Type: ,File size (bytes): 4402,Device ID: USBSTOR\Disk&Ven_TOSHIBA&Prod_External_USB_3.0&REV_9020141571855308750352033"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
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

#<50>Apr 14 10:10:10 SymantecServer: xxx,Site: Site_C,Server Name: C1560245824,Domain Name: Domain_C,Admin: Admin_C,Event Description: Package properties have been changed
def test_symantec_ep_admin_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},Site: Site_C,Server Name: C1560245824,Domain Name: Domain_C,Admin: Admin_C,Event Description: Package properties have been changed"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:admin:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:10:10 SymantecServer: xxx,C2560867323,Local Host IP: 127.0.0.1,Local Port: 21351,Remote Host IP: 127.0.0.1,Remote Host Name: ,Remote Port: 25343,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed
def test_symantec_ep_packet_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},C2560867323,Local Host IP: 127.0.0.1,Local Port: 21351,Remote Host IP: 127.0.0.1,Remote Host Name: ,Remote Port: 25343,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:packet:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:10:10 SymantecServer: xxx,Site: Site_D,Server Name: C1560245824,Domain Name: Domain_D,Admin: Admin_D,Event Description: Policy has been edited: Changed location-independent policy or settings.,Client Policy
def test_symantec_ep_policy_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},Site: Site_D,Server Name: C1560245824,Domain Name: Domain_D,Admin: Admin_D,Event Description: Policy has been edited: Changed location-independent policy or settings.,Client Policy"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:policy:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:10:10 SymantecServer: xxx,D1560245728,Event Description: "Web Attack: Mass Iframe Injection Website 17",Event Type: Active Response was disengaged,Local Host IP: 127.0.0.1,Local Host MAC: 3f17Fd119cC5,Remote Host Name: AB7R7F9G9-GHSIW9,Remote Host IP: 127.0.0.1,Remote Host MAC: bee3134665eB,Unknown,TCP,,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Occurrences: 1,Application: C:/Windows/System32/example_x.exe,Location: External,User Name: user210,Domain Name: local,Local Port: 14171,Remote Port: 44770,CIDS Signature ID: 28865,CIDS Signature string: Informational: HTTP PE Download,CIDS Signature SubID: 68433,Intrusion URL: https://www.example.org/,Intrusion Payload URL: db-76.thompson.info,SHA-256: 3a0a04e61f20fb39f76198f59dbe3e3a2173107c1f7adaa020b2e56a8d549877,MD-5: d57f21e6a273781dbf8b7657940f3b03,Intensive Protection Level: 2,URL Risk: Possibly malicious,URL Category: Social Networking
def test_symantec_ep_security_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} SymantecServer: {{ host }},D1560245728,Event Description: "Web Attack: Mass Iframe Injection Website 17",Event Type: Active Response was disengaged,Local Host IP: 127.0.0.1,Local Host MAC: 3f17Fd119cC5,Remote Host Name: AB7R7F9G9-GHSIW9,Remote Host IP: 127.0.0.1,Remote Host MAC: bee3134665eB,Unknown,TCP,,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Occurrences: 1,Application: C:/Windows/System32/example_x.exe,Location: External,User Name: user210,Domain Name: local,Local Port: 14171,Remote Port: 44770,CIDS Signature ID: 28865,CIDS Signature string: Informational: HTTP PE Download,CIDS Signature SubID: 68433,Intrusion URL: https://www.example.org/,Intrusion Payload URL: db-76.thompson.info,SHA-256: 3a0a04e61f20fb39f76198f59dbe3e3a2173107c1f7adaa020b2e56a8d549877,MD-5: d57f21e6a273781dbf8b7657940f3b03,Intensive Protection Level: 2,URL Risk: Possibly malicious,URL Category: Social Networking'
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:security:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:10:10 SymantecServer: xxx,Virus found,IP Address: 127.0.0.1,Computer name: V1201V-UATMQ01,Source: Heuristic Scan,Risk name: WS.Reputation.1,Occurrences: 4,File path: c:\\users\\userx\u0007ppdata\\local\\mmmmmm\\yyyos\temporary internet files\\content.ie5\\obouj877,Description: ,Actual action: Left alone,Requested action: Cleaned,Secondary action: Quarantined,Event time: 2021-03-10 11:14:39,Event Insert Time: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Last update time: 2021-03-10 11:14:39,Domain Name: Default,Group Name: \Default Group,Server Name: C1560245824,User Name: user179,Source Computer Name: cvprdwebbppv002,Source Computer IP: 127.0.0.1,Disposition: Reputation was not used in this detection.,Download site: https://art.example.com/advice/animal,Web domain: lt-83.fitzgerald.com,Downloaded by: null,Prevalence: Reputation was not used in this detection.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: ,Allowed application reason: MDS,Application hash: 246c39b4-6421-4244-86be-b65af400b445,Hash type: SHA1,Company name: JJJJJ,Application name: ,Application version: ,Application type: Trojan Worm,File size (bytes): 8322,Category set: ,Category type: UNKNOWN,Location: Default,Intensive Protection Level: 1,Certificate issuer: GoDaddy,Certificate signer: GoDaddy,Certificate thumbprint: 23:xx:94:94:5x:95:f2:41:xx:03:xx:bb:zz:d2:a3:a3:f5:d8:8b:xx,Signing timestamp: 0,Certificate serial number: 314531972711909413743075096039378935511
def test_symantec_ep_risk_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},Virus found,IP Address: 127.0.0.1,Computer name: V1201V-UATMQ01,Source: Heuristic Scan,Risk name: WS.Reputation.1,Occurrences: 4,File path: c:\\users\\userx\u0007ppdata\\local\\mmmmmm\\yyyos\temporary internet files\\content.ie5\\obouj877,Description: ,Actual action: Left alone,Requested action: Cleaned,Secondary action: Quarantined,Event time: 2021-03-10 11:14:39,Event Insert Time: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Last update time: 2021-03-10 11:14:39,Domain Name: Default,Group Name: \Default Group,Server Name: C1560245824,User Name: user179,Source Computer Name: cvprdwebbppv002,Source Computer IP: 127.0.0.1,Disposition: Reputation was not used in this detection.,Download site: https://art.example.com/advice/animal,Web domain: lt-83.fitzgerald.com,Downloaded by: null,Prevalence: Reputation was not used in this detection.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: ,Allowed application reason: MDS,Application hash: 246c39b4-6421-4244-86be-b65af400b445,Hash type: SHA1,Company name: JJJJJ,Application name: ,Application version: ,Application type: Trojan Worm,File size (bytes): 8322,Category set: ,Category type: UNKNOWN,Location: Default,Intensive Protection Level: 1,Certificate issuer: GoDaddy,Certificate signer: GoDaddy,Certificate thumbprint: 23:xx:94:94:5x:95:f2:41:xx:03:xx:bb:zz:d2:a3:a3:f5:d8:8b:xx,Signing timestamp: 0,Certificate serial number: 314531972711909413743075096039378935511"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:risk:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <50>Apr 14 10:10:10 SymantecServer: xxx,C2560867323,Local Host IP: 127.0.0.1,Local Port: 10502,Local Host MAC: c9DeaEb57Fed,Remote Host IP: 127.0.0.1,Remote Host Name: NXI00APPVAPV001,Remote Port: 52674,Remote Host MAC: D7e8dcB5587F,others,Inbound,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Occurrences: 9,Application: C:/Windows/System32/example_x.exe,Rule: Allow IGMP traffic,Location: Public Network,User Name: user216,Domain Name: IC,Action: Allowed,SHA-256: ,MD-5:
def test_symantec_ep_traffic_v14_3_33RU1(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} SymantecServer: {{ host }},C2560867323,Local Host IP: 127.0.0.1,Local Port: 10502,Local Host MAC: c9DeaEb57Fed,Remote Host IP: 127.0.0.1,Remote Host Name: NXI00APPVAPV001,Remote Port: 52674,Remote Host MAC: D7e8dcB5587F,others,Inbound,Begin: 2021-03-10 11:14:39,End Time: 2021-03-10 11:14:39,Occurrences: 9,Application: C:/Windows/System32/example_x.exe,Rule: Allow IGMP traffic,Location: Public Network,User Name: user216,Domain Name: IC,Action: Allowed,SHA-256: ,MD-5:"
    )
    message = mt.render(mark="<50>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:traffic:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
