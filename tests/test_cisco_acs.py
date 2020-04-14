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

def test_cisco_acs_single(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ACS
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]


    mt = env.from_string(
    "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Passed_Authentications 0765855540 1 0 {{ date }} {{ time }} {{ tzoffset }} 0178632943 5202 NOTICE Device-Administration: Command Authorization succeeded, ACSVersion=acs-5.8.1.4-B.462.x86_64, ConfigVersionId=16489, Device IP Address=10.0.0.93, DestinationIPAddress=10.0.0.10, DestinationPort=49, UserName=nsdevman, CmdSet=[ CmdAV=show CmdArgAV=vpn-sessiondb CmdArgAV=full CmdArgAV=ra-ikev2-ipsec ], Protocol=Tacacs, MatchedCommandSet=fw3, RequestLatency=11, Type=Authorization, Privilege-Level=15, Authen-Type=ASCII, Service=None, User=nsdevman, Port=443, Remote-Address=10.0.0.15, Authen-Method=TacacsPlus, Service-Argument=shell, AcsSessionID=mnsvdcfpiuac03/359448835/9871764, AuthenticationIdentityStore=AD1, AuthenticationMethod=Lookup, SelectedAccessService=Default Device Admin, SelectedCommandSet=fw3, IdentityGroup=IdentityGroup:All Groups:SystemID, Step=13005 , Step=15008 , Step=15004 , Step=15012 , Step=15041 , Step=15004 , Step=15013 , Step=24210 , Step=24212 , Step=24432 , Step=24325 , Step=24313 , Step=24319 , Step=24323 , Step=24420 , Step=24355 , Step=24416 , Step=22037 , Step=15044 , Step=15035 , Step=15042 , Step=15036 , Step=15004 , Step=15018 , Step=13024 , Step=13034 , SelectedAuthenticationIdentityStores=Internal Users, NetworkDeviceName=devicenamehere, NetworkDeviceGroups=Device Type:All Device Types:Firewall:Cisco Systems:Firewall:ASA5545, NetworkDeviceGroups=Location:All Locations:MN, ServiceSelectionMatchedRule=TACACS, IdentityPolicyMatchedRule=Firewall, AuthorizationPolicyMatchedRule=nsdevman, AD-User-Candidate-Identities=nsdevman@ent.example.corp, AD-User-DNS-Domain=ent.example.corp, AD-User-NetBios-Name=AD-ENT, AD-User-Resolved-Identities=nsdevman@ent.example.corp, AD-User-Join-Point=ENT.example.CORP, AD-User-Resolved-DNs=CN=nsdevman\,OU=Service Accounts\,OU=CAO\,OU=ENT\,DC=ent\,DC=wfb\,DC=example\,DC=corp, StepData=10=nsdevman, StepData=11=ent.example.corp, StepData=12=example.corp, StepData=15=ent.example.corp, AD-Domain=ent.example.corp, IdentityAccessRestricted=false, UserIdentityGroup=IdentityGroup:All Groups:SystemID, Cisco-Firewall=Superuser, Firewall=Superuser, NetSec-CSM=User, NetSec-Logging=Engineer, Response={Type=Authorization; Author-Reply-Status=PassAdd; ExternalIdentityStoreName=AD1; }\n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netauth host=\"{{ host }}\" sourcetype=\"cisco:acs\"")
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_cisco_acs_multi(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ACS
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Passed_Authentications 0000000002 2 0 {{ date }} {{ time }} {{ tzoffset }} 0000008450 5203 NOTICE Device-Administration: Session Authorization succeeded, ACSVersion=acs-5.2.0.26-B.3075, ConfigVersionId=117, Device IP Address=192.168.26.137, UserName=edward, CmdSet=[ CmdAV= ], Protocol=Tacacs, RequestLatency=10, NetworkDeviceName=switch, Type=Authorization, Privilege-Level=1, Authen-Type=ASCII, Service=Login, User=edward, Port=tty2, Remote-Address=10.78.167.190, Authen-Method=TacacsPlus, Service-Argument=shell, AcsSessionID=ACS41/101085887/112, AuthenticationIdentityStore=Internal Users, AuthenticationMethod=Lookup, SelectedAccessService=Default Device Admin, SelectedShellProfile=Permit Access, IdentityGroup=IdentityGroup:All Groups, Step=13005 , Step=15008 , Step=15004 , Step=15012 , Step=15041 , Step=15006 , Step=15013 , Step=24210 , Step=24212 , Step=22037 , Step=15044 , Step=15035 , Step=15042 , Step=15036 , Step=15004 , Step=15017 , Step=13034 , \n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    # Generate new datetime for second message; not used in log path parser so actually could be anything
    dt = datetime.datetime.now() + datetime.timedelta(seconds=1)
    bsd = dt.strftime("%b %d %H:%M:%S")

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Passed_Authentications 0000000002 2 1 Step=13015 , SelectedAuthenticationIdentityStores=Internal Users, NetworkDeviceGroups=s1Migrated_NDGs:All s1Migrated_NDGs, NetworkDeviceGroups=Device Type:All Device Types, NetworkDeviceGroups=Location:All Locations, ServiceSelectionMatchedRule=Rule-2, IdentityPolicyMatchedRule=Default, AuthorizationPolicyMatchedRule=Rule-0, Action=Login, Privilege-Level=1, Authen-Type=ASCII, Service=Login, Remote-Address=10.78.167.190, UserIdentityGroup=IdentityGroup:All\n")
    message = mt.render(mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netauth host=\"{{ host }}\" sourcetype=\"cisco:acs\" \"Step=13015\"")
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
