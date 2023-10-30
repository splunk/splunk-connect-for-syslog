# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <13>Jan 18 11:07:53 192.168.1.1 LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# Jan 18 11:07:53 myhostname LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5 cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <13>Jan 18 11:07:53 192.168.1.1 LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
# Jan 18 11:07:53 myhostname LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
testdata1 = [
    "{{ mark }}{{ bsd }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
    "{{ bsd }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:1.0|Palo Alto Networks|PAN-OS Syslog Integration|8.1.8|allow|cat=TRAFFIC|ReceiveTime=2020/09/03 09:54:59|SerialNumber=012345678912|Type=TRAFFIC|Subtype=end|devTime=Sep 03 2020 14:54:59 GMT|src=1.1.1.1|dst=1.1.1.1|srcPostNAT=0.0.0.0|dstPostNAT=0.0.0.0|RuleName=test|usrName=|SourceUser=|DestinationUser=|Application=incomplete|VirtualSystem=vsys1|SourceZone=test|DestinationZone=test|IngressInterface=test|EgressInterface=test|LogForwardingProfile=Log to Panorama|SessionID=test|RepeatCount=1|srcPort=12345|dstPort=443|srcPostNATPort=0|dstPostNATPort=0|Flags=0x19|proto=tcp|action=allow|totalBytes=60|dstBytes=0|srcBytes=60|totalPackets=1|StartTime=2020/09/03 09:54:53|ElapsedTime=0|URLCategory=any|sequence=6694316277998249989|ActionFlags=0x8000000000000000|SourceLocation=United States|DestinationLocation=United States|dstPackets=0|srcPackets=1|SessionEndReason=aged-out|DeviceGroupHierarchyL1=117|DeviceGroupHierarchyL2=118|DeviceGroupHierarchyL3=119|DeviceGroupHierarchyL4=146|vSrcName=vsys1|DeviceName=host|ActionSource=from-policy|SrcUUID=|DstUUID=|TunnelID=0|MonitorTag=|ParentSessionID=0|ParentStartTime=|TunnelType=N/A'",
]
# <13>1 2019-01-18T11:07:53.520Z 192.168.1.1 LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <133>1 2019-01-18T11:07:53.520+07:00 myhostname LEEF:1.0|Microsoft|MSExchange|4.0 SP1|15345|src=192.0.2.0 dst=172.50.123.1 sev=5cat=anomaly srcPort=81 dstPort=21 usrName=joe.black
# <13>1 2019-01-18T11:07:53.520Z 192.168.1.1 LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
# <133>1 2019-01-18T11:07:53.520+07:00 myhostname LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
testdata2 = [
    "{{ mark }}{{ bsd }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ bsd }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|0x5E|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|x5E|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID||src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
    "{{ mark }}1 {{ iso }} {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|src=200.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black",
]
# The following samples test "raw time" parsing
testdata3 = [
    "{{ mark }} Jan  1 01:01:00 {{ host }} LEEF:1.0|Vendor|Product|Version|EventID|src=192.0.2.0\tdst=172.50.123.1\tsev=5\tcat=anomaly\tsrcPort=81\tdstPort=21\tusrName=joe.black\tdevTime={{ epoch }}",
    "{{ mark }}1 2022-01-18T11:01:53.520Z {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=200.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black^devTime={{ epoch }}",
    "{{ mark }}1 2022-01-18T11:02:53.520Z {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=200.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black^devTime={{ epoch }}^devTimeFormat=",
    "{{ mark }}1 2022-01-18T11:03:53.520Z {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=200.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black^devTime={{ bsd }}^devTimeFormat=MMM dd yyyy HH:mm:ss",
    "{{ mark }}1 2022-01-18T11:04:53.520Z {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=200.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black^devTime={{ bsd }}.000^devTimeFormat=MMM dd yyyy HH:mm:ss.SSS",
    "{{ mark }}1 2022-01-18T11:05:53.520Z {{ host }} LEEF:2.0|Vendor|Product|Version|EventID|^|src=200.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black^devTime={{ bsd }}.000 EST^devTimeFormat=MMM dd yyyy HH:mm:ss.SSS z",
]

@pytest.mark.lite
@pytest.mark.parametrize("event", testdata1)
def test_leef1_generic(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = iso[0:19] + iso[26:32]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="LEEF:1"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.lite
@pytest.mark.parametrize("event", testdata2)
def test_leef2_generic(
    record_property,  setup_splunk, setup_sc4s, event
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = iso[0:19] + iso[26:32]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="LEEF:2:*"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.lite
@pytest.mark.parametrize("event", testdata3)
def test_leef_devtime(record_property,  setup_splunk, setup_sc4s, event):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = iso[0:19] + iso[26:32]
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="LEEF:*"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
