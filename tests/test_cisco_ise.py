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

#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 0 2019-04-24 15:00:48.610 +00:00 0042009748 5200 NOTICE Passed-Authentication: Authentication succeeded, ConfigVersionId=128, Device IP Address=10.6.64.15, DestinationIPAddress=10.16.20.23, DestinationPort=1812, UserName=90-1B-0E-34-EA-92, Protocol=Radius, RequestLatency=8, NetworkDeviceName=ICPAV2-SW15, User-Name=901b0e34ea92, NAS-IP-Address=10.6.64.15, NAS-Port=50104, Service-Type=Call Check, Framed-IP-Address=10.6.226.138, Framed-MTU=1500, Called-Station-ID=B0-FA-EB-11-70-04, Calling-Station-ID=90-1B-0E-34-EA-92, NAS-Port-Type=Ethernet, NAS-Port-Id=GigabitEthernet0/4, EAP-Key-Name=, cisco-av-pair=service-type=Call Check, cisco-av-pair=audit-session-id=0A06400F000006AA6F83C371, cisco-av-pair=method=mab, OriginalUserName=901b0e34ea92, NetworkDeviceProfileName=Cisco, NetworkDeviceProfileId=b2652f13-5b3f-41ba-ada2-8385c8870809, IsThirdPartyDeviceFlow=false, RadiusFlowType=WiredMAB, SSID=B0-FA-EB-11-70-04,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 1  AcsSessionID=ICDC-ISE03/341048949/1407358, AuthenticationIdentityStore=Internal Endpoints, AuthenticationMethod=Lookup, SelectedAccessService=Default Network Access, SelectedAuthorizationProfiles=WIRED_GUEST_REDIRECT, UseCase=Host Lookup, IdentityGroup=Endpoint Identity Groups:Unknown, Step=11001, Step=11017, Step=11027, Step=15049, Step=15008, Step=15048, Step=15048, Step=15041, Step=15013, Step=24209, Step=24211, Step=22037, Step=24715, Step=15036, Step=15048, Step=15048, Step=15016, Step=11002, SelectedAuthenticationIdentityStores=Internal Endpoints, AuthenticationStatus=AuthenticationPassed, NetworkDeviceGroups=Location#All Locations#Provo, NetworkDeviceGroups=Device Type#All Device Types#Switches, NetworkDeviceGroups=Migrated NDGs#All Migrated NDGs, IdentityPolicyMatchedRule=Default, AuthorizationPolicyMatchedRule=Guest Web Auth, UserType=Host, CPMSessionID=0A06400F000006AA6F83C371, EndPointMACAddress=90-1B-0E-34-EA-92,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 2  PostureAssessmentStatus=NotApplicable, EndPointMatchedProfile=Unknown, DeviceRegistrationStatus=notRegistered, ISEPolicySetName=Wired MAB, IdentitySelectionMatchedRule=Default, StepData=5= Aruba.Aruba-Essid-Name, StepData=6= DEVICE.Device Type, StepData=8=Internal Endpoints, StepData=14= EndPoints.LogicalProfile, StepData=15= Network Access.Protocol, allowEasyWiredSession=false, DTLSSupport=Unknown, HostIdentityGroup=Endpoint Identity Groups:Unknown, Network Device Profile=Cisco, Location=Location#All Locations#Provo, Device Type=Device Type#All Device Types#Switches, Migrated NDGs=Migrated NDGs#All Migrated NDGs, Name=Endpoint Identity Groups:Unknown,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 3  Response={UserName=90:1B:0E:34:EA:92; User-Name=90-1B-0E-34-EA-92; State=ReauthSession:0A06400F000006AA6F83C371; Class=CACS:0A06400F000006AA6F83C371:ICDC-ISE03/341048949/1407358; Session-Timeout=300; Idle-Timeout=240; Termination-Action=RADIUS-Request; cisco-av-pair=url-redirect-acl=ACL-WEBAUTH-REDIRECT; cisco-av-pair=url-redirect=https://ICDC-ISE03.example.com:8443/portal/gateway?sessionId=0A06400F000006AA6F83C371&portal=c5a76cb0-6150-11e5-b062-0050568d954e&action=cwa&type=drw&token=6ded1943789b345f7afdd09e91549047; cisco-av-pair=profile-name=Unknown; LicenseTypes=1; },

def test_cisco_ise_multi(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ISE
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CISE_Passed_Authentications 0001939187 4 0 {{ date }} {{ time }} {{ tzoffset }} 0042009748 5200 NOTICE Passed-Authentication: Authentication succeeded, ConfigVersionId=128, Device IP Address=10.6.64.15, DestinationIPAddress=10.16.20.23, DestinationPort=1812, UserName=90-1B-0E-34-EA-92, Protocol=Radius, RequestLatency=8, NetworkDeviceName=ICPAV2-SW15, User-Name=901b0e34ea92, NAS-IP-Address=10.6.64.15, NAS-Port=50104, Service-Type=Call Check, Framed-IP-Address=10.6.226.138, Framed-MTU=1500, Called-Station-ID=B0-FA-EB-11-70-04, Calling-Station-ID=90-1B-0E-34-EA-92, NAS-Port-Type=Ethernet, NAS-Port-Id=GigabitEthernet0/4, EAP-Key-Name=, cisco-av-pair=service-type=Call Check, cisco-av-pair=audit-session-id=0A06400F000006AA6F83C371, cisco-av-pair=method=mab, OriginalUserName=901b0e34ea92, NetworkDeviceProfileName=Cisco, NetworkDeviceProfileId=b2652f13-5b3f-41ba-ada2-8385c8870809, IsThirdPartyDeviceFlow=false, RadiusFlowType=WiredMAB, SSID=B0-FA-EB-11-70-04,\n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    # Generate new datetime for subsequent messages; not used in log path parser so actually could be anything
    dt = datetime.datetime.now() + datetime.timedelta(seconds=1)
    bsd = dt.strftime("%b %d %H:%M:%S")

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CISE_Passed_Authentications 0001939187 4 1  AcsSessionID=ICDC-ISE03/341048949/1407358, AuthenticationIdentityStore=Internal Endpoints, AuthenticationMethod=Lookup, SelectedAccessService=Default Network Access, SelectedAuthorizationProfiles=WIRED_GUEST_REDIRECT, UseCase=Host Lookup, IdentityGroup=Endpoint Identity Groups:Unknown, Step=11001, Step=11017, Step=11027, Step=15049, Step=15008, Step=15048, Step=15048, Step=15041, Step=15013, Step=24209, Step=24211, Step=22037, Step=24715, Step=15036, Step=15048, Step=15048, Step=15016, Step=11002, SelectedAuthenticationIdentityStores=Internal Endpoints, AuthenticationStatus=AuthenticationPassed, NetworkDeviceGroups=Location#All Locations#Provo, NetworkDeviceGroups=Device Type#All Device Types#Switches, NetworkDeviceGroups=Migrated NDGs#All Migrated NDGs, IdentityPolicyMatchedRule=Default, AuthorizationPolicyMatchedRule=Guest Web Auth, UserType=Host, CPMSessionID=0A06400F000006AA6F83C371, EndPointMACAddress=90-1B-0E-34-EA-92,\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CISE_Passed_Authentications 0001939187 4 2  PostureAssessmentStatus=NotApplicable, EndPointMatchedProfile=Unknown, DeviceRegistrationStatus=notRegistered, ISEPolicySetName=Wired MAB, IdentitySelectionMatchedRule=Default, StepData=5= Aruba.Aruba-Essid-Name, StepData=6= DEVICE.Device Type, StepData=8=Internal Endpoints, StepData=14= EndPoints.LogicalProfile, StepData=15= Network Access.Protocol, allowEasyWiredSession=false, DTLSSupport=Unknown, HostIdentityGroup=Endpoint Identity Groups:Unknown, Network Device Profile=Cisco, Location=Location#All Locations#Provo, Device Type=Device Type#All Device Types#Switches, Migrated NDGs=Migrated NDGs#All Migrated NDGs, Name=Endpoint Identity Groups:Unknown,\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CISE_Passed_Authentications 0001939187 4 3  Response={UserName=90:1B:0E:34:EA:92; User-Name=90-1B-0E-34-EA-92; State=ReauthSession:0A06400F000006AA6F83C371; Class=CACS:0A06400F000006AA6F83C371:ICDC-ISE03/341048949/1407358; Session-Timeout=300; Idle-Timeout=240; Termination-Action=RADIUS-Request; cisco-av-pair=url-redirect-acl=ACL-WEBAUTH-REDIRECT; cisco-av-pair=url-redirect=https://ICDC-ISE03.example.com:8443/portal/gateway?sessionId=0A06400F000006AA6F83C371&portal=c5a76cb0-6150-11e5-b062-0050568d954e&action=cwa&type=drw&token=6ded1943789b345f7afdd09e91549047; cisco-av-pair=profile-name=Unknown; LicenseTypes=1; },\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netauth host=\"{{ host }}\" sourcetype=\"cisco:ise:syslog\" LicenseTypes=1")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<181>Oct 24 21:00:02 ciscohost CISE_RADIUS_Accounting 0006028545 1 0 2019-10-24 21:00:02.305 +00:00 0088472694 3002 NOTICE Radius-Accounting: RADIUS Accounting watchdog update, ConfigVersionId=336, Device IP Address=10.0.0.3, RequestLatency=3, NetworkDeviceName=nc-aaa-aaa1, User-Name=U100000.ent.corp, NAS-IP-Address=10.0.0.3, NAS-Port=50047, Service-Type=Framed, Framed-IP-Address=10.0.0.80, Class=CACS:0AEF12345677832097B3F362:ncsilsepsuie212/356139633/9969901, Called-Station-ID=00-08-00-00-1B-AF, Calling-Station-ID=00-00-00-00-A0-7E, Acct-Status-Type=Interim-Update, Acct-Delay-Time=0, Acct-Input-Octets=653293631, Acct-Output-Octets=1497972244, Acct-Session-Id=00000B68, Acct-Authentic=RADIUS, Acct-Session-Time=241598, Acct-Input-Packets=2656224, Acct-Output-Packets=7614179, Acct-Input-Gigawords=0, Acct-Output-Gigawords=1, NAS-Port-Type=Ethernet, NAS-Port-Id=FastEthernet0/47, undefined-151=31D7AADD, cisco-av-pair=audit-session-id=0AEF10030000032097B3F362, cisco-av-pair=connect-progress=Auth Open, AcsSessionID=ncsilsepsuie205/359238109/4017186, SelectedAccessService=Default Network Access, Step=11004, Step=11017, Step=15049, Step=15008, Step=15048, Step=15048, Step=15048, Step=15004, Step=22094, Step=11005, NetworkDeviceGroups=Location#All Locations#NC, NetworkDeviceGroups=Device Type#All Device Types#Switch#2960-Switches, NetworkDeviceGroups=All Network Device Groups#All Network Device Groups, CPMSessionID=0AEF10030000032097B3F362, AllowedProtocolMatchedRule=EAP-TLS, All Network Device Groups=All Network Device Groups#All Network Device Groups, Location=Location#All Locations#NC, Device Type=Device Type#All Device Types#Switch#2960-Switches, Network Device Profile=Cisco,
def test_cisco_ise_single(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ISE
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CISE_RADIUS_Accounting 0006028545 1 0 {{ date }} {{ time }} {{ tzoffset }} 0088472694 3002 NOTICE Radius-Accounting: RADIUS Accounting watchdog update, ConfigVersionId=336, Device IP Address=10.0.0.3, RequestLatency=3, NetworkDeviceName=nc-aaa-aaa1, User-Name=U100000.ent.corp, NAS-IP-Address=10.0.0.3, NAS-Port=50047, Service-Type=Framed, Framed-IP-Address=10.0.0.80, Class=CACS:0AEF12345677832097B3F362:ncsilsepsuie212/356139633/9969901, Called-Station-ID=00-08-00-00-1B-AF, Calling-Station-ID=00-00-00-00-A0-7E, Acct-Status-Type=Interim-Update, Acct-Delay-Time=0, Acct-Input-Octets=653293631, Acct-Output-Octets=1497972244, Acct-Session-Id=00000B68, Acct-Authentic=RADIUS, Acct-Session-Time=241598, Acct-Input-Packets=2656224, Acct-Output-Packets=7614179, Acct-Input-Gigawords=0, Acct-Output-Gigawords=1, NAS-Port-Type=Ethernet, NAS-Port-Id=FastEthernet0/47, undefined-151=31D7AADD, cisco-av-pair=audit-session-id=0AEF10030000032097B3F362, cisco-av-pair=connect-progress=Auth Open, AcsSessionID=ncsilsepsuie205/359238109/4017186, SelectedAccessService=Default Network Access, Step=11004, Step=11017, Step=15049, Step=15008, Step=15048, Step=15048, Step=15048, Step=15004, Step=22094, Step=11005, NetworkDeviceGroups=Location#All Locations#NC, NetworkDeviceGroups=Device Type#All Device Types#Switch#2960-Switches, NetworkDeviceGroups=All Network Device Groups#All Network Device Groups, CPMSessionID=0AEF10030000032097B3F362, AllowedProtocolMatchedRule=EAP-TLS, All Network Device Groups=All Network Device Groups#All Network Device Groups, Location=Location#All Locations#NC, Device Type=Device Type#All Device Types#Switch#2960-Switches, Network Device Profile=Cisco,\n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netauth host=\"{{ host }}\" sourcetype=\"cisco:ise:syslog\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
