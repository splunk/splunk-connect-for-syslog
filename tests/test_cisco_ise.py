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

#Sep  4 00:02:23 t-na-e-dc-4 CISE_Failed_Attempts 0002079848 3 0 2012-09-04 00:02:23.307 -05:00 0069172882 5400 NOTICE Failed-Attempt: Authentication failed, ConfigVersionId=14, Device IP Address=10.2.25.10, Device Port=32768, DestinationIPAddress=10.7.1.28, DestinationPort=1812, RadiusPacketType=AccessRequest, UserName=mat67746, Protocol=Radius, RequestLatency=1, NetworkDeviceName=ti-svc-wi_b-dc-3, User-Name=test, NAS-IP-Address=10.2.25.160, NAS-Port=29, Service-Type=Framed, Framed-MTU=1300, State=37CPMSessionID=0ae4ffa00003898250457d50\;43SessionID=ts-na-e-c-4/134430/295\;, Called-Station-ID=00-00-00-00-00-00, Calling-Station-ID=0c-04-00-00-00-00, NAS-Identifier=tis-w_bw-dc-3, NAS-Port-Type=Wireless - IEEE 802.11, Tunnel-Type=(tag=0) VLAN, Tunnel-Medium-Type=(tag=0) 802, Tunnel-Private-Group-ID=(tag=0) 3002, cisco-av-pair=audit-session-id=0ae4ffd50, Airespace-Wlan-Id=1, AcsSessionID=tis-n-i-dc-4/134439/2950,
#Sep  4 00:02:23 t-na-e-dc-4 CISE_Failed_Attempts 0002079848 3 1  SelectedAccessService=Default Network Access, FailureReason=12321 PEAP failed SSL/TLS handshake because the client rejected the ISE local-certificate, Step=11001, Step=11017, Step=15008, Step=15048, Step=15048, Step=15004, Step=11507, Step=12500, Step=11006, Step=11001, Step=11018, Step=12301, Step=12300, Step=11006, Step=11001, Step=11018, Step=12302, Step=12319, Step=12800, Step=12805, Step=12806, Step=12807, Step=12810, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12319, Step=12815, Step=12321, Step=12307, Step=11504, Step=11003, NetworkDeviceGroups=Device Type#All Device Types#Wireless Controllers, NetworkDeviceGroups=Location#All Locations#, ServiceSelectionMatchedRule=Dot1X_Wireless, EapTunnel=PEAP,
#Sep  4 00:02:23 t-na-e-dc-4 CISE_Failed_Attempts 0002079848 3 2  OpenSSLErrorMessage=SSL alert: code=0x230=560 \; source=remote \; type=fatal \; message="unknown CA", OpenSSLErrorStack=  120492:error:14418:SSL routines:SSL3_READ_BYTES:tlsv1 alert unknown ca:s3_pkt.c:1102:SSL alert number 48, CPMSessionID=0ae4fd50, EndPointMACAddress=00-00-00-00-00-00, Device Type=Device Type#All Device Types#Wireless Controllers, Location=Location#All Locations, Response={RadiusPacketType=AccessReject; },
def test_cisco_ise(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Failed_Attempts 0002079848 3 0 2012-09-04 00:02:23.307 -05:00 0069172882 5400 NOTICE Failed-Attempt: Authentication failed, ConfigVersionId=14, Device IP Address=10.2.25.10, Device Port=32768, DestinationIPAddress=10.7.1.28, DestinationPort=1812, RadiusPacketType=AccessRequest, UserName=mat67746, Protocol=Radius, RequestLatency=1, NetworkDeviceName=ti-svc-wi_b-dc-3, User-Name=test, NAS-IP-Address=10.2.25.160, NAS-Port=29, Service-Type=Framed, Framed-MTU=1300, State=37CPMSessionID=0ae4ffa00003898250457d50\;43SessionID=ts-na-e-c-4/134430/295\;, Called-Station-ID=00-00-00-00-00-00, Calling-Station-ID=0c-04-00-00-00-00, NAS-Identifier=tis-w_bw-dc-3, NAS-Port-Type=Wireless - IEEE 802.11, Tunnel-Type=(tag=0) VLAN, Tunnel-Medium-Type=(tag=0) 802, Tunnel-Private-Group-ID=(tag=0) 3002, cisco-av-pair=audit-session-id=0ae4ffd50, Airespace-Wlan-Id=1, AcsSessionID=tis-n-i-dc-4/134439/2950,\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Failed_Attempts 0002079848 3 1  SelectedAccessService=Default Network Access, FailureReason=12321 PEAP failed SSL/TLS handshake because the client rejected the ISE local-certificate, Step=11001, Step=11017, Step=15008, Step=15048, Step=15048, Step=15004, Step=11507, Step=12500, Step=11006, Step=11001, Step=11018, Step=12301, Step=12300, Step=11006, Step=11001, Step=11018, Step=12302, Step=12319, Step=12800, Step=12805, Step=12806, Step=12807, Step=12810, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12319, Step=12815, Step=12321, Step=12307, Step=11504, Step=11003, NetworkDeviceGroups=Device Type#All Device Types#Wireless Controllers, NetworkDeviceGroups=Location#All Locations#, ServiceSelectionMatchedRule=Dot1X_Wireless, EapTunnel=PEAP,\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Failed_Attempts 0002079848 3 2  OpenSSLErrorMessage=SSL alert: code=0x230=560 \\; source=remote \\; type=fatal \\; message=\"unknown CA\", OpenSSLErrorStack=  120492:error:14418:SSL routines:SSL3_READ_BYTES:tlsv1 alert unknown ca:s3_pkt.c:1102:SSL alert number 48, CPMSessionID=0ae4fd50, EndPointMACAddress=00-00-00-00-00-00, Device Type=Device Type#All Device Types#Wireless Controllers, Location=Location#All Locations, Response={RadiusPacketType=AccessReject; },\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:ise\" | head 11")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
