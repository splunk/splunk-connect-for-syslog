# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

# Mar 19 15:19:15 syslog1 CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:050|Connector Raw Event Statistics|Low| eventId=77 mrt=1539321422787 categorySignificance=/Informational categoryBehavior=/Execute/Response categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321424798 cat=/Agent/RawEvent/Statistics deviceSeverity=Warning rt=1539321422787 fileType=Agent cs1=0.23 cs2=157.72333333333333 cs3=0.23 cs4=47317 cs5=157.72333333333333 cs6=3o0OiZmYBABCACGN9CiyuGQ\=\= cn1=69 cn2=47317 cn3=69 deviceCustomDate1=1539321122775 cs1Label=Event throughput cs2Label=Raw event character throughput cs3Label=Event throughput (SLC) cs4Label=Raw event length (SLC) cs5Label=Raw event character throughput (SLC) cs6Label=Destination ID cn1Label=Total event count cn2Label=Total raw event length cn3Label=Event count (SLC) deviceCustomDate1Label=Last time ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=
# Mar 19 15:19:15 syslog1 CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:016|Device connection up|Low| eventId=30 msg=Connected to Host mrt=1539321123071 categorySignificance=/Normal categoryBehavior=/Access/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321124967 cat=/Agent/Connection/Device?Success deviceSeverity=Warning rt=1539321123071 dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 fileType=Agent cs2=<Resource ID\="3MQ1+L2YBABCAApZ7fvr37A\=\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=
# Mar 19 15:19:15 root CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:030|Agent [PAN1_WUC_UDP8000] type [windowsfg] started|Low| eventId=26 mrt=1539321122832 categorySignificance=/Normal categoryBehavior=/Execute/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application/Service art=1539321124967 cat=/Agent/Started deviceSeverity=Warning rt=1539321122832 fileType=Agent cs2=<Resource ID\="3MQ1+L2YBABCAApZ7fvr37A\=\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=
# Mar 19 15:19:15 syslog1 CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:016|Device connection up|Low| eventId=77 msg=Connected to Host mrt=1539321047341 categorySignificance=/Normal categoryBehavior=/Access/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321049259 cat=/Agent/Connection/Device?Success deviceSeverity=Warning rt=1539321047341 dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 fileType=Agent cs2=<Resource ID\="3MQ1+L2YBABCAApZ7fvr37A\=\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=
def test_microfocus_arcsight_cef_ts_rt(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:016|Device connection up|Low| eventId=77 msg=Connected to Host mrt=1539321047341 categorySignificance=/Normal categoryBehavior=/Access/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321049259 cat=/Agent/Connection/Device?Success deviceSeverity=Warning rt=' + "{% now 'utc', '%s' %}" + ' dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 fileType=Agent cs2=<Resource ID\\="3MQ1+L2YBABCAApZ7fvr37A\\=\\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\\=\\=' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=ArcSight:ArcSight | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_microfocus_arcsight_cef_ts_end(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:016|Device connection up|Low| eventId=77 msg=Connected to Host mrt=1539321047341 categorySignificance=/Normal categoryBehavior=/Access/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321049259 cat=/Agent/Connection/Device?Success deviceSeverity=Warning end=' + "{% now 'utc', '%s' %}" + ' dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 fileType=Agent cs2=<Resource ID\\="3MQ1+L2YBABCAApZ7fvr37A\\=\\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\\=\\=' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=ArcSight:ArcSight| head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_microfocus_arcsight_cef_ts_syslog(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|ArcSight|ArcSight|7.9.0.8084.0|agent:016|Device connection up|Low| eventId=77 msg=Connected to Host mrt=1539321047341 categorySignificance=/Normal categoryBehavior=/Access/Start categoryDeviceGroup=/Application catdt=Security Management categoryOutcome=/Success categoryObject=/Host/Application art=1539321049259 cat=/Agent/Connection/Device?Success deviceSeverity=Warning dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 fileType=Agent cs2=<Resource ID\\="3MQ1+L2YBABCAApZ7fvr37A\\=\\="/> cs2Label=Configuration Resource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=win-pan1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dvcmac=00-0C-29-98-8D-D7 dtz=Asia/Riyadh _cefVer=0.1 aid=3o0OiZmYBABCACGN9CiyuGQ\\=\\=' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=ArcSight:ArcSight | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_microfocus_arcsight_windows(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|Microsoft|Microsoft Windows||Microsoft-Windows-Security-Auditing:4634|An account was logged off.|Low| eventId=1 externalId=4634 msg=Network: A user or computer logged on to this computer from the network. rawEvent=EventlogType\=Security&&EventIndex\=1031&&WindowsVersion\=Windows Server 2012 R2&&WindowsKeyMapFamily\=Windows 2012 R2&&WindowsParserFamily\=Windows 2012 R2|2012|8&&DetectTime\=2018-10-12 7:25:11&&EventSource\=Microsoft-Windows-Security-Auditing&&EventID\=4634&&EventType\=Audit_success&&EventCategory\=12545&&User\=null&&ComputerName\=WIN-PAN1&&Description\=An account was logged off.&&Message\=This event is generated when a logon session is destroyed. It may be positively correlated with a logon event using the Logon ID value. Logon IDs are only unique between reboots on the same computer.&&Subject:Security ID\=S-1-5-21-750061412-3179291162-3140434184-500&&Subject:Account Name\=Administrator&&Subject:Account Domain\=WIN-PAN1&&Subject:Logon ID\=0x373c2&&Logon Type\=3 categorySignificance=/Informational categoryBehavior=/Access/Stop categoryDeviceGroup=/Operating System catdt=Operating System categoryOutcome=/Success categoryObject=/Host/Operating System art=1539321047369 cat=Security deviceSeverity=Audit_success rt=' + "{% now 'utc', '%s' %}" + ' dhost=WIN-PAN1 dst=192.168.13.152 destinationZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dntdom=WIN-PAN1 duser=Administrator duid=0x373c2 cs2=Logon/Logoff:Logoff cn1=3 cs1Label=Accesses cs2Label=EventlogCategory cs4Label=Reason or Error Code cs5Label=Authentication Package Name cn1Label=LogonType cn2Label=CrashOnAuditFail cn3Label=Count ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=WIN-PAN1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 deviceNtDomain=WIN-PAN1 dtz=Asia/Riyadh _cefVer=0.1 ad.WindowsVersion=Windows Server 2012 R2 ad.WindowsParserFamily=Windows 2012 R2|2012|8 ad.WindowsKeyMapFamily=Windows 2012 R2 ad.EventIndex=1031 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=\"CEFEventLog:Microsoft Windows\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_microfocus_arcsight_windows_system(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|Microsoft|System or Application Event||Software Protection Platform Service:902|Software Protection Platform Service|Unknown| eventId=39 externalId=902 rawEvent=EventlogType\=Application&&EventIndex\=1604&&WindowsVersion\=Windows Server 2012 R2&&WindowsKeyMapFamily\=Windows 2012 R2&&WindowsParserFamily\=Windows 2012 R2|2012|8&&DetectTime\=2018-10-12 8:12:31&&EventSource\=Software Protection Platform Service&&EventID\=902&&EventType\=null&&EventCategory\=0&&User\=null&&ComputerName\=WIN-PAN1&&Key[0]\=6.3.9600.16384 art=1539321151610 cat=Application rt=' + "{% now 'utc', '%s' %}" + ' cs2=0 cs3=Software Protection Platform Service cs2Label=EventlogCategory cs3Label=EventSource ahost=win-pan1 agt=192.168.13.152 agentZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 amac=00-0C-29-98-8D-D7 av=7.9.0.8084.0 atz=Asia/Riyadh at=windowsfg dvchost=WIN-PAN1 dvc=192.168.13.152 deviceZoneURI=/All Zones/ArcSight System/Private Address Space Zones/RFC1918: 192.168.0.0-192.168.255.255 dtz=Asia/Riyadh _cefVer=0.1 ad.WindowsVersion=Windows Server 2012 R2 ad.WindowsParserFamily=Windows 2012 R2|2012|8 ad.WindowsKeyMapFamily=Windows 2012 R2 ad.Key[0]=6.3.9600.16384 ad.EventIndex=1604 aid=3o0OiZmYBABCACGN9CiyuGQ\=\=' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=\"CEFEventLog:System or Application Event\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_microfocus_arcsight_imperva_incapsula(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%b %d %H:%M:%S' %} {{ host }} " + 'CEF:0|Incapsula|SIEMintegration|1|1|Illegal Resource Access|3| fileid=3412341160002518171 sourceServiceName=site123.abcd.info siteid=1509732 suid=50005477 requestClientApplication=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0 deviceFacility=mia cs2=true cs2Label=Javascript Support cs3=true cs3Label=CO Support src=12.12.12.12 caIP=13.13.13.13 ccode=IL tag=www.elvis.com cn1=200 in=54 xff=44.44.44.44 cs1=NOT_SUPPORTED cs1Label=Cap Support cs4=c2e72124-0e8a-4dd8-b13b-3da246af3ab2 cs4Label=VID cs5=de3c633ac428e0678f3aac20cf7f239431e54cbb8a17e8302f53653923305e1835a9cd871db32aa4fc7b8a9463366cc4 cs5Label=clappsigdproc=Browser cs6=Firefox cs6Label=clapp ccode=IL cicode=Rehovot cs7=31.8969 cs7Label=latitude cs8=34.8186 cs8Label=longitude Customer=CEFcustomer123 ver=TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 start=1453290121336 request=site123.abcd.info/ requestmethod=GET qstr=p\=%2fetc%2fpasswd app=HTTP act=REQ_CHALLENGE_CAPTCHA deviceExternalID=33411452762204224 cpt=443 filetype=30037,1001, filepermission=2,1, cs9=Block Malicious User,High Risk Resources, cs9Label=Rule name' + "\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cef\" source=\"Imperva:Incapsula\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1