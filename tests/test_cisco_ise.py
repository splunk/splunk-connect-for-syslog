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

#PV¼¡EØgÙ%CEúÌ@?ú

#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 0 2019-04-24 15:00:48.610 +00:00 0042009748 5200 NOTICE Passed-Authentication: Authentication succeeded, ConfigVersionId=128, Device IP Address=10.6.64.15, DestinationIPAddress=10.16.20.23, DestinationPort=1812, UserName=90-1B-0E-34-EA-92, Protocol=Radius, RequestLatency=8, NetworkDeviceName=ICPAV2-SW15, User-Name=901b0e34ea92, NAS-IP-Address=10.6.64.15, NAS-Port=50104, Service-Type=Call Check, Framed-IP-Address=10.6.226.138, Framed-MTU=1500, Called-Station-ID=B0-FA-EB-11-70-04, Calling-Station-ID=90-1B-0E-34-EA-92, NAS-Port-Type=Ethernet, NAS-Port-Id=GigabitEthernet0/4, EAP-Key-Name=, cisco-av-pair=service-type=Call Check, cisco-av-pair=audit-session-id=0A06400F000006AA6F83C371, cisco-av-pair=method=mab, OriginalUserName=901b0e34ea92, NetworkDeviceProfileName=Cisco, NetworkDeviceProfileId=b2652f13-5b3f-41ba-ada2-8385c8870809, IsThirdPartyDeviceFlow=false, RadiusFlowType=WiredMAB, SSID=B0-FA-EB-11-70-04,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 1  AcsSessionID=ICDC-ISE03/341048949/1407358, AuthenticationIdentityStore=Internal Endpoints, AuthenticationMethod=Lookup, SelectedAccessService=Default Network Access, SelectedAuthorizationProfiles=WIRED_GUEST_REDIRECT, UseCase=Host Lookup, IdentityGroup=Endpoint Identity Groups:Unknown, Step=11001, Step=11017, Step=11027, Step=15049, Step=15008, Step=15048, Step=15048, Step=15041, Step=15013, Step=24209, Step=24211, Step=22037, Step=24715, Step=15036, Step=15048, Step=15048, Step=15016, Step=11002, SelectedAuthenticationIdentityStores=Internal Endpoints, AuthenticationStatus=AuthenticationPassed, NetworkDeviceGroups=Location#All Locations#Provo, NetworkDeviceGroups=Device Type#All Device Types#Switches, NetworkDeviceGroups=Migrated NDGs#All Migrated NDGs, IdentityPolicyMatchedRule=Default, AuthorizationPolicyMatchedRule=Guest Web Auth, UserType=Host, CPMSessionID=0A06400F000006AA6F83C371, EndPointMACAddress=90-1B-0E-34-EA-92,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 2  PostureAssessmentStatus=NotApplicable, EndPointMatchedProfile=Unknown, DeviceRegistrationStatus=notRegistered, ISEPolicySetName=Wired MAB, IdentitySelectionMatchedRule=Default, StepData=5= Aruba.Aruba-Essid-Name, StepData=6= DEVICE.Device Type, StepData=8=Internal Endpoints, StepData=14= EndPoints.LogicalProfile, StepData=15= Network Access.Protocol, allowEasyWiredSession=false, DTLSSupport=Unknown, HostIdentityGroup=Endpoint Identity Groups:Unknown, Network Device Profile=Cisco, Location=Location#All Locations#Provo, Device Type=Device Type#All Device Types#Switches, Migrated NDGs=Migrated NDGs#All Migrated NDGs, Name=Endpoint Identity Groups:Unknown,
#<165>Apr 24 15:00:48 ICDC-ISE03 CISE_Passed_Authentications 0001939187 4 3  Response={UserName=90:1B:0E:34:EA:92; User-Name=90-1B-0E-34-EA-92; State=ReauthSession:0A06400F000006AA6F83C371; Class=CACS:0A06400F000006AA6F83C371:ICDC-ISE03/341048949/1407358; Session-Timeout=300; Idle-Timeout=240; Termination-Action=RADIUS-Request; cisco-av-pair=url-redirect-acl=ACL-WEBAUTH-REDIRECT; cisco-av-pair=url-redirect=https://ICDC-ISE03.example.com:8443/portal/gateway?sessionId=0A06400F000006AA6F83C371&portal=c5a76cb0-6150-11e5-b062-0050568d954e&action=cwa&type=drw&token=6ded1943789b345f7afdd09e91549047; cisco-av-pair=profile-name=Unknown; LicenseTypes=1; },

def test_cisco_ise(record_property, setup_wordlist, setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Passed_Authentications 0001939187 4 0 {% now 'utc', '%Y-%m-%d %H:%M:%S' %}.610 +00:00 0042009748 5200 NOTICE Passed-Authentication: Authentication succeeded, ConfigVersionId=128, Device IP Address=10.6.64.15, DestinationIPAddress=10.16.20.23, DestinationPort=1812, UserName=90-1B-0E-34-EA-92, Protocol=Radius, RequestLatency=8, NetworkDeviceName=ICPAV2-SW15, User-Name=901b0e34ea92, NAS-IP-Address=10.6.64.15, NAS-Port=50104, Service-Type=Call Check, Framed-IP-Address=10.6.226.138, Framed-MTU=1500, Called-Station-ID=B0-FA-EB-11-70-04, Calling-Station-ID=90-1B-0E-34-EA-92, NAS-Port-Type=Ethernet, NAS-Port-Id=GigabitEthernet0/4, EAP-Key-Name=, cisco-av-pair=service-type=Call Check, cisco-av-pair=audit-session-id=0A06400F000006AA6F83C371, cisco-av-pair=method=mab, OriginalUserName=901b0e34ea92, NetworkDeviceProfileName=Cisco, NetworkDeviceProfileId=b2652f13-5b3f-41ba-ada2-8385c8870809, IsThirdPartyDeviceFlow=false, RadiusFlowType=WiredMAB, SSID=B0-FA-EB-11-70-04,\n")
    message = mt.render(mark="<165>", host=host)
    sendsingle(message)

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Passed_Authentications 0001939187 4 1  AcsSessionID=ICDC-ISE03/341048949/1407358, AuthenticationIdentityStore=Internal Endpoints, AuthenticationMethod=Lookup, SelectedAccessService=Default Network Access, SelectedAuthorizationProfiles=WIRED_GUEST_REDIRECT, UseCase=Host Lookup, IdentityGroup=Endpoint Identity Groups:Unknown, Step=11001, Step=11017, Step=11027, Step=15049, Step=15008, Step=15048, Step=15048, Step=15041, Step=15013, Step=24209, Step=24211, Step=22037, Step=24715, Step=15036, Step=15048, Step=15048, Step=15016, Step=11002, SelectedAuthenticationIdentityStores=Internal Endpoints, AuthenticationStatus=AuthenticationPassed, NetworkDeviceGroups=Location#All Locations#Provo, NetworkDeviceGroups=Device Type#All Device Types#Switches, NetworkDeviceGroups=Migrated NDGs#All Migrated NDGs, IdentityPolicyMatchedRule=Default, AuthorizationPolicyMatchedRule=Guest Web Auth, UserType=Host, CPMSessionID=0A06400F000006AA6F83C371, EndPointMACAddress=90-1B-0E-34-EA-92,\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Passed_Authentications 0001939187 4 2  PostureAssessmentStatus=NotApplicable, EndPointMatchedProfile=Unknown, DeviceRegistrationStatus=notRegistered, ISEPolicySetName=Wired MAB, IdentitySelectionMatchedRule=Default, StepData=5= Aruba.Aruba-Essid-Name, StepData=6= DEVICE.Device Type, StepData=8=Internal Endpoints, StepData=14= EndPoints.LogicalProfile, StepData=15= Network Access.Protocol, allowEasyWiredSession=false, DTLSSupport=Unknown, HostIdentityGroup=Endpoint Identity Groups:Unknown, Network Device Profile=Cisco, Location=Location#All Locations#Provo, Device Type=Device Type#All Device Types#Switches, Migrated NDGs=Migrated NDGs#All Migrated NDGs, Name=Endpoint Identity Groups:Unknown,\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %} {{ host }} CISE_Passed_Authentications 0001939187 4 3  Response={UserName=90:1B:0E:34:EA:92; User-Name=90-1B-0E-34-EA-92; State=ReauthSession:0A06400F000006AA6F83C371; Class=CACS:0A06400F000006AA6F83C371:ICDC-ISE03/341048949/1407358; Session-Timeout=300; Idle-Timeout=240; Termination-Action=RADIUS-Request; cisco-av-pair=url-redirect-acl=ACL-WEBAUTH-REDIRECT; cisco-av-pair=url-redirect=https://ICDC-ISE03.example.com:8443/portal/gateway?sessionId=0A06400F000006AA6F83C371&portal=c5a76cb0-6150-11e5-b062-0050568d954e&action=cwa&type=drw&token=6ded1943789b345f7afdd09e91549047; cisco-av-pair=profile-name=Unknown; LicenseTypes=1; },\n")
    message = mt.render(mark="<111>", host=host)
    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"cisco:ise:syslog\" | head 11")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
