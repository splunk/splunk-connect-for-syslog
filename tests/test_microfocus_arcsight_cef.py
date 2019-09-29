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