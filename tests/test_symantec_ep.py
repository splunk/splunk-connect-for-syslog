# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

test_data = [
    "{{ mark }}{{ bsd }} {{host}} SymantecServer: Site: Site xxxxx,Server Name: xxxxx,Domain Name: Default,The management server received the client log successfully,yyyyyyy,zzzzzzzz,host.domain.suffix",
    "{{ mark }}{{ bsd }} {{host}} SymantecServer: Site: Site xxxxx,Server Name: xxxxx,Domain Name: Default,Client has downloaded the issued Command,yyyyyyy,zzzzzzzz,host.domain.suffix",
]


@pytest.mark.addons("broadcom")
@pytest.mark.parametrize("event", test_data)
def test_symantec_ep_agent(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<134>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:agent:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:41:51 xxxxx-xxxxx SymantecServer: yyyyyy,Category: 2,LiveUpdate Manager,Event Description: A LiveUpdate session ran successfully.  No new updates were available.,Event time: 2020-04-14 10:41:33,Group Name: My Company\Default Group
@pytest.mark.addons("broadcom")
def test_symantec_ep_agt_system(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: yyyyyy,Category: 2,LiveUpdate Manager,Event Description: A LiveUpdate session ran successfully.  No new updates were available.,Event time: 2020-04-14 10:41:33,Group Name: My Company\Default Group"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:agt:system:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 09:07:42 xxxxx-xxxxx SymantecServer: Site: Site xxxxx-xxxxx,Server Name: xxxxx-xxxxx,Event Description: No updates found for Application Control Data 14.2 RU2.
@pytest.mark.addons("broadcom")
def test_symantec_ep_scm_system(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + "SymantecServer: Site: Site xxxxx-xxxxx,Server Name: xxxxx-xxxxx,Event Description: No updates found for Application Control Data 14.2 RU2."
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:scm:system:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:03:23 xxxxx-xxxxx SymantecServer: Scan ID: 1581582179,Begin: 2020-04-14 10:01:04,End Time: 2020-04-14 10:02:14,Completed,Duration (seconds): 70,User1: Spiderman,User2: Spiderman,Scan started on selected drives and folders and all extensions.,Scan Complete:  Risks: 0   Scanned: 1062   Files/Folders/Drives Omitted: 0 Trusted Files Skipped: 698,Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 1062,Omitted: 0,Computer: yyyyyyy,IP Address: 1.1.1.1,Domain Name: Default,Group Name: My Company\Preprod Tuesday,Server Name: xxxxx-xxxxx
@pytest.mark.addons("broadcom")
def test_symantec_ep_scan(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: Scan ID: 1581582179,Begin: 2020-04-14 10:01:04,End Time: 2020-04-14 10:02:14,Completed,Duration (seconds): 70,User1: Spiderman,User2: Spiderman,Scan started on selected drives and folders and all extensions.,Scan Complete:  Risks: 0   Scanned: 1062   Files/Folders/Drives Omitted: 0 Trusted Files Skipped: 698,Command: Not a command scan (),Threats: 0,Infected: 0,Total files: 1062,Omitted: 0,Computer: yyyyyyy,IP Address: 1.1.1.1,Domain Name: Default,Group Name: My Company\Preprod Tuesday,Server Name: xxxxx-xxxxx"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:scan:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:42:32 xxxxx-xxxxx SymantecServer: yyyyyy,...,Blocked,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,,Begin: 2020-04-14 10:36:40,End Time: 2020-04-14 10:36:40,Rule: ,3248,C:\PROGRAM FILES (X86)\BIGFIX ENTERPRISE\BES CLIENT\BESCLIENT.EXE,0,,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,User Name: SYSTEM,Domain Name: ,Action Type: 55,File size (bytes): ,Device ID:
@pytest.mark.addons("broadcom")
def test_symantec_ep_behavior(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: yyyyyy,...,Blocked,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,,Begin: 2020-04-14 10:36:40,End Time: 2020-04-14 10:36:40,Rule: ,3248,C:\PROGRAM FILES (X86)\BIGFIX ENTERPRISE\BES CLIENT\BESCLIENT.EXE,0,,C:\Program Files (x86)\Symantec\Symantec Endpoint Protection\14.2.3335.1000.105\Bin\ccSvcHst.exe,User Name: SYSTEM,Domain Name: ,Action Type: 55,File size (bytes): ,Device ID: "
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:behavior:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,Event Description: Administrator log on failed
@pytest.mark.addons("broadcom")
def test_symantec_ep_admin(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,Event Description: Administrator log on failed"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:admin:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: ccccc,Local Host IP: 10.0.8.1,Local Port: 50221,Remote Host IP: 10.0.1.2,Remote Host Name: qqqqq,Remote Port: 20362,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed
@pytest.mark.addons("broadcom")
def test_symantec_ep_packet(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: ccccc,Local Host IP: 10.0.8.1,Local Port: 50221,Remote Host IP: 10.0.1.2,Remote Host Name: qqqqq,Remote Port: 20362,Outbound,Application: C:/Windows/System32/example_y.exe,Action: Allowed"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:packet:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,"Event Description: Policy has been edited: Changed Console mode at [Default]",Client Policy
@pytest.mark.addons("broadcom")
def test_symantec_ep_policy(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r'SymantecServer: Site: Site_B,Server Name: Example Server B,Domain Name: Domain_B,Admin: Admin_B,"Event Description: Policy has been edited: Changed Console mode at [Default]",Client Policy'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:policy:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: Potential risk found,Computer name: ooooo,IP Address: 10.0.0.2,Detection type: System Change HostFile,First Seen: Symantec has known about this file for more than 1 year.,Application name: Microsoft\xAE Windows\xAE Operating System,Application type: 127,Application version: 6.1.7600.16385,Hash type: SHA-256,Application hash: ded6fc40-4365-4ba0-8446-3fa77a30cb6e,Company name: KKK.,LLLL,MMMM,File size (bytes): 3507,Sensitivity: 2,Detection score: 3,COH Engine Version: ,Detection Submissions No,Permitted application reason: Not on the permitted application list,Disposition: Bad,Download site: http://attraction.example.org/,Web domain: tkhwesmptszdody.dm,Downloaded by: c:/users/administrator/desktop/tools/tools/xxxtools.exe,Prevalence: Unknown,Confidence: There is not enough information about this file to recommend it.,URL Tracking Status: on,Risk Level: High,Risk type: 3,Source: Heuristic Scan,Risk name: Trojan.Gen.2,Occurrences: 9,PolicyZZZ,Realtime deferred scanning,Actual action: Left alone,Requested action: Quarantined,Secondary action: Left alone,Event time: 2020-05-04 06:57:02,Inserted: 2020-05-04 06:57:02,End: 2020-05-04 06:57:02,Domain: Domain A,Group: My Company\Default Group,Server: Example Server C,User: user_b,Source computer: fffff,Source IP: 10.0.9.2,Intensive Protection Level: 0,Certificate issuer: Symantec,Certificate signer: Unizeto,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 149843929435818692848040365716851702463
@pytest.mark.addons("broadcom")
def test_symantec_ep_proactive(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: Potential risk found,Computer name: ooooo,IP Address: 10.0.0.2,Detection type: System Change HostFile,First Seen: Symantec has known about this file for more than 1 year.,Application name: Microsoft\xAE Windows\xAE Operating System,Application type: 127,Application version: 6.1.7600.16385,Hash type: SHA-256,Application hash: ded6fc40-4365-4ba0-8446-3fa77a30cb6e,Company name: KKK.,LLLL,MMMM,File size (bytes): 3507,Sensitivity: 2,Detection score: 3,COH Engine Version: ,Detection Submissions No,Permitted application reason: Not on the permitted application list,Disposition: Bad,Download site: http://attraction.example.org/,Web domain: tkhwesmptszdody.dm,Downloaded by: c:/users/administrator/desktop/tools/tools/xxxtools.exe,Prevalence: Unknown,Confidence: There is not enough information about this file to recommend it.,URL Tracking Status: on,Risk Level: High,Risk type: 3,Source: Heuristic Scan,Risk name: Trojan.Gen.2,Occurrences: 9,PolicyZZZ,Realtime deferred scanning,Actual action: Left alone,Requested action: Quarantined,Secondary action: Left alone,Event time: 2020-05-04 06:57:02,Inserted: 2020-05-04 06:57:02,End: 2020-05-04 06:57:02,Domain: Domain A,Group: My Company\Default Group,Server: Example Server C,User: user_b,Source computer: fffff,Source IP: 10.0.9.2,Intensive Protection Level: 0,Certificate issuer: Symantec,Certificate signer: Unizeto,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 149843929435818692848040365716851702463"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:proactive:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: qqqqq,Event Description: "Web Attack: Fake Scan Webpage 7",Local Host IP: 10.0.3.4,Local Host MAC: c1411f5F9502,Remote Host Name: eeeee,Remote Host IP: 10.0.3.6,Remote Host MAC: aD31CCFD3eFF,Inbound,TCP,Intrusion ID: 1,Begin: 2020-05-06 09:06:09,End Time: 2020-05-06 09:06:09,Occurrences: 3,Application: C:/Windows/System32/example_x.exe,Location: Internal,User Name: user_h,Domain Name: CompanyXX,Local Port: 1991,Remote Port: 46926,CIDS Signature ID: 25198,CIDS Signature string: Web Attack: Fake Scan Webpage 7,CIDS Signature SubID: 25378,Intrusion URL: https://www.example.org/,Intrusion Payload URL: http://www.example.com/,SHA-256: 6d2fe32dc4249ef7e7359c6d874fffbbf335e832e49a2681236e1b686af78794,MD-5: 70270ca63a3de2d8905a9181a0245e58
@pytest.mark.addons("broadcom")
def test_symantec_ep_security(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r'SymantecServer: qqqqq,Event Description: "Web Attack: Fake Scan Webpage 7",Local Host IP: 10.0.3.4,Local Host MAC: c1411f5F9502,Remote Host Name: eeeee,Remote Host IP: 10.0.3.6,Remote Host MAC: aD31CCFD3eFF,Inbound,TCP,Intrusion ID: 1,Begin: 2020-05-06 09:06:09,End Time: 2020-05-06 09:06:09,Occurrences: 3,Application: C:/Windows/System32/example_x.exe,Location: Internal,User Name: user_h,Domain Name: CompanyXX,Local Port: 1991,Remote Port: 46926,CIDS Signature ID: 25198,CIDS Signature string: Web Attack: Fake Scan Webpage 7,CIDS Signature SubID: 25378,Intrusion URL: https://www.example.org/,Intrusion Payload URL: http://www.example.com/,SHA-256: 6d2fe32dc4249ef7e7359c6d874fffbbf335e832e49a2681236e1b686af78794,MD-5: 70270ca63a3de2d8905a9181a0245e58'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:security:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: Security risk found,IP Address: 10.0.3.1,Computer name: qqqqq,Source: Definition downloader,Risk name: Backdoor.Joggver,Occurrences: 7,e:\resharper 9.1 + keygen\resharper.8.x.keygen.exe,"Still contains, 2 infected items",Actual action: Quarantined,Requested action: Process terminate pending restartLeft alone,Secondary action: Quarantined,Event time: 2020-05-06 08:29:27,Inserted: 2020-05-06 08:29:27,End: 2020-05-06 08:29:27,Last update time: 2020-05-06 08:29:27,Domain: SomeComp,Group: My Company\\Default Group,Server: Example Server C,User: user_h,Source computer: hhhhh,Source IP: 10.0.4.1,Disposition: Reputation was not used in this detection.,Download site: http://bbbb.example.com/,Web domain: gqtavlakkdkcryl.xn--pgbs0dh,Downloaded by: c:/program files (x86)/ggggg/cccc/application/cccc.exe,Prevalence: This file has been seen by fewer than 100 Symantec users.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: low,MDS,Application hash: 44d7fb7e-8c40-4a17-9aff-9c4aa0b96696,Hash type: SHA1,Company name: "Sample Inc. a wholly owned subsidiary of Dummy, Inc.",Application name: Setup Factory 7.0 Runtime,Application version: ,Application type: 127,File size (bytes): 1318,Category set: Security risk,Category type: UNKNOWN,Location: AZ - Office,Intensive Protection Level: 0,Certificate issuer: "Realtime deferred scanning",Certificate signer: Comodo,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 903804111
@pytest.mark.addons("broadcom")
def test_symantec_ep_risk(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r'SymantecServer: Security risk found,IP Address: 10.0.3.1,Computer name: qqqqq,Source: Definition downloader,Risk name: Backdoor.Joggver,Occurrences: 7,e:\resharper 9.1 + keygen\resharper.8.x.keygen.exe,"Still contains, 2 infected items",Actual action: Quarantined,Requested action: Process terminate pending restartLeft alone,Secondary action: Quarantined,Event time: 2020-05-06 08:29:27,Inserted: 2020-05-06 08:29:27,End: 2020-05-06 08:29:27,Last update time: 2020-05-06 08:29:27,Domain: SomeComp,Group: My Company\\Default Group,Server: Example Server C,User: user_h,Source computer: hhhhh,Source IP: 10.0.4.1,Disposition: Reputation was not used in this detection.,Download site: http://bbbb.example.com/,Web domain: gqtavlakkdkcryl.xn--pgbs0dh,Downloaded by: c:/program files (x86)/ggggg/cccc/application/cccc.exe,Prevalence: This file has been seen by fewer than 100 Symantec users.,Confidence: There is growing evidence that this file is trustworthy.,URL Tracking Status: off,First Seen: Reputation was not used in this detection.,Sensitivity: low,MDS,Application hash: 44d7fb7e-8c40-4a17-9aff-9c4aa0b96696,Hash type: SHA1,Company name: "Sample Inc. a wholly owned subsidiary of Dummy, Inc.",Application name: Setup Factory 7.0 Runtime,Application version: ,Application type: 127,File size (bytes): 1318,Category set: Security risk,Category type: UNKNOWN,Location: AZ - Office,Intensive Protection Level: 0,Certificate issuer: "Realtime deferred scanning",Certificate signer: Comodo,Certificate thumbprint: e5:xx:74:3c:xx:01:c4:9b:xx:43:xx:bb:zz:e8:6a:81:10:9f:e4:xx,Signing timestamp: 0,Certificate serial number: 903804111'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:risk:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Apr 14 10:10:10 dummyhost SymantecServer: nnnnn,Local Host IP: 10.0.0.2,Local Port: 10456,Local Host MAC: B9e90F5c3aC4,Remote Host IP: 10.0.9.2,Remote Host Name: lllll,Remote Port: 58999,Remote Host MAC: 7b6A329f7c1e,others,Inbound,Begin: 2020-05-06 09:18:32,End: 2020-05-06 09:18:32,Occurrences: 8,Application: C:/Windows/System32/example_y.EXE,Rule: Block all other IP traffic and log,Location: Public Network,User: user_f,Domain: XXXXDOMAIN,Action: Blocked,SHA-256: d1616b874a96df2515da372a90bddc00792cbff027f5e097cafa31d3aea8b310,MD-5: 82136b4240d6ce4ea7d03e51469a393b
@pytest.mark.addons("broadcom")
def test_symantec_ep_traffic(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{host}} "
        + r"SymantecServer: nnnnn,Local Host IP: 10.0.0.2,Local Port: 10456,Local Host MAC: B9e90F5c3aC4,Remote Host IP: 10.0.9.2,Remote Host Name: lllll,Remote Port: 58999,Remote Host MAC: 7b6A329f7c1e,others,Inbound,Begin: 2020-05-06 09:18:32,End: 2020-05-06 09:18:32,Occurrences: 8,Application: C:/Windows/System32/example_y.EXE,Rule: Block all other IP traffic and log,Location: Public Network,User: user_f,Domain: XXXXDOMAIN,Action: Blocked,SHA-256: d1616b874a96df2515da372a90bddc00792cbff027f5e097cafa31d3aea8b310,MD-5: 82136b4240d6ce4ea7d03e51469a393b"
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="symantec:ep:traffic:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
