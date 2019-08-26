# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

# <165>1 2007-02-15T09:17:15.719Z router1 mgd 3046 UI_DBASE_LOGOUT_EVENT [junos@2636.1.1.1.2.18 username="user"] User 'user' exiting configuration mode
# @pytest.mark.xfail
def test_juniper_junos_structured(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%S' %}.700Z {{ host }} mgd 3046 UI_DBASE_LOGOUT_EVENT [junos@2636.1.1.1.2.18 username=\"user\"] User 'user' exiting configuration mode\n")
    message = mt.render(mark="<165>1", host=host)

    sendsingle(message)

    st = env.from_string("search index=main host=\"{{ host }}\" sourcetype=\"juniper:structured\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <165>1 2007-02-15T09:17:15.719Z idp1 RT_IDP - IDP_ATTACK_LOG_EVENT [junos@2636.1.1.1.2.135 epoch-time="1507845354" message-type="SIG" source-address="183.78.180.27" source-port="45610" destination-address="118.127.xx.xx" destination-port="80" protocol-name="TCP" service-name="SERVICE_IDP" application-name="HTTP" rule-name="9" rulebase-name="IPS" policy-name="Recommended" export-id="15229" repeat-count="0" action="DROP" threat-severity="HIGH" attack-name="TROJAN:ZMEU-BOT-SCAN" nat-source-address="0.0.0.0" nat-source-port="0" nat-destination-address="172.xx.xx.xx" nat-destination-port="0" elapsed-time="0" inbound-bytes="0" outbound-bytes="0" inbound-packets="0" outbound-packets="0" source-zone-name="sec-zone-name-internet" source-interface-name="reth0.XXX" destination-zone-name="dst-sec-zone1-outside" destination-interface-name="reth1.xxx" packet-log-id="0" alert="no" username="N/A" roles="N/A" message="-"]
# @pytest.mark.xfail
def test_juniper_junos_idp_structured(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%S' %}.700Z {{ host }} RT_IDP - IDP_ATTACK_LOG_EVENT [junos@2636.1.1.1.2.135 epoch-time=\"1507845354\" message-type=\"SIG\" source-address=\"183.78.180.27\" source-port=\"45610\" destination-address=\"118.127.xx.xx\" destination-port=\"80\" protocol-name=\"TCP\" service-name=\"SERVICE_IDP\" application-name=\"HTTP\" rule-name=\"9\" rulebase-name=\"IPS\" policy-name=\"Recommended\" export-id=\"15229\" repeat-count=\"0\" action=\"DROP\" threat-severity=\"HIGH\" attack-name=\"TROJAN:ZMEU-BOT-SCAN\" nat-source-address=\"0.0.0.0\" nat-source-port=\"0\" nat-destination-address=\"172.xx.xx.xx\" nat-destination-port=\"0\" elapsed-time=\"0\" inbound-bytes=\"0\" outbound-bytes=\"0\" inbound-packets=\"0\" outbound-packets=\"0\" source-zone-name=\"sec-zone-name-internet\" source-interface-name=\"reth0.XXX\" destination-zone-name=\"dst-sec-zone1-outside\" destination-interface-name=\"reth1.xxx\" packet-log-id=\"0\" alert=\"no\" username=\"N/A\" roles=\"N/A\" message=\"-\"]")
    message = mt.render(mark="<165>1", host=host)

    sendsingle(message)

    st = env.from_string("search index=netids host=\"{{ host }}\" sourcetype=\"juniper:junos:idp:structured\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <165>1 2010-06-23T18:05:55 10.209.83.9 Jnpr Syslog 23414 1 [syslog@juniper.net dayId="20100623" recordId="0" timeRecv="2010/06/23 18:05:55" timeGen="2010/06/23 18:05:51" domain="" devDomVer2="0" device_ip="10.209.83.9" cat="Config" attack="" srcZn="NULL" srcIntf="" srcAddr="0.0.0.0" srcPort="0" natSrcAddr="NULL" natSrcPort="0" dstZn="NULL" dstIntf="NULL" dstAddr="0.0.0.0" dstPort="0" natDstAddr="NULL" natDstPort="0" protocol="IP" ruleDomain="" ruleVer="0" policy="" rulebase="NONE" ruleNo="0" action="NONE" severity="INFO" alert="no" elaspedTime="0" inbytes="0" outbytes="0" totBytes="0" inPak="0" outPak="0" totPak="0" repCount="0" packetData="no" varEnum="0" misc="Interaface  eth2,eth3 is in Normal State" user="NULL" app="NULL" uri="NULL"]
# <THIS TEST TENTATIVE PENDING A VALID DATA SAMPLE; NEEDED TO OMIT THE "1" IN THIS TEST SAMPLE (BEFORE [] BLOCK) TO GET IT TO PARSE 5424>
# <VALIDATE BEFORE SHIPPING!>
# <THIS TEST MAY NEED TO BE REWRITTEN AS A "STANDARD" TEST IF THE DATA IS ACTUALLY SENT IN 3164 FORMAT>
# @pytest.mark.xfail
def test_juniper_idp_structured(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%S' %}.700Z {{ host }} Jnpr Syslog 23414 [syslog@juniper.net dayId=\"20100623\" recordId=\"0\" timeRecv=\"2010/06/23 18:05:55\" timeGen=\"2010/06/23 18:05:51\" domain=\"\" devDomVer2=\"0\" device_ip=\"10.209.83.9\" cat=\"Config\" attack=\"\" srcZn=\"NULL\" srcIntf=\"\" srcAddr=\"0.0.0.0\" srcPort=\"0\" natSrcAddr=\"NULL\" natSrcPort=\"0\" dstZn=\"NULL\" dstIntf=\"NULL\" dstAddr=\"0.0.0.0\" dstPort=\"0\" natDstAddr=\"NULL\" natDstPort=\"0\" protocol=\"IP\" ruleDomain=\"\" ruleVer=\"0\" policy=\"\" rulebase=\"NONE\" ruleNo=\"0\" action=\"NONE\" severity=\"INFO\" alert=\"no\" elaspedTime=\"0\" inbytes=\"0\" outbytes=\"0\" totBytes=\"0\" inPak=\"0\" outPak=\"0\" totPak=\"0\" repCount=\"0\" packetData=\"no\" varEnum=\"0\" misc=\"Interaface  eth2,eth3 is in Normal State\" user=\"NULL\" app=\"NULL\" uri=\"NULL\"]")
    message = mt.render(mark="<165>1", host=host)

    sendsingle(message)

    st = env.from_string("search index=netids host=\"{{ host }}\" sourcetype=\"juniper:idp:structured\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <134> Aug 02 14:45:04 10.0.0.1 65.197.254.193 20090320, 17331, 2009/03/20 14:47:45, 2009/03/20 14:47:50, global, 53, [FW NAME], [FW IP], traffic, traffic log, trust, (NULL), 10.1.1.20, 1725, 82.2.19.2, 2383, untrust, (NULL), 84.5.78.4, 80, 84.53.178.64, 80, tcp, global, 53, [FW NAME], fw/vpn, 4, accepted, info, no, Creation, (NULL), (NULL), (NULL), 0, 0, 0, 0, 0, 0, 0, 1, no, 0, Not Set, sos
# @pytest.mark.xfail
def test_juniper_junos_fw_structured(record_property, setup_wordlist, get_host_key, setup_splunk):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'utc', '%Y-%m-%dT%H:%M:%S' %}.700Z {{ host }} RT_FLOW - RT_FLOW_SESSION_CREATE_LS [junos@2636.1.1.1.2.26 logical-system-name=\"test-lsys\" source-address=\"10.10.10.100\" source-port=\"4206\" destination-address=\"10.20.20.15\" destination-port=\"445\" service-name=\"junos-smb\" nat-source-address=\"10.10.10.100\" nat-source-port=\"4206\" nat-destination-address=\"10.20.20.15\" nat-destination-port=\"445\" src-nat-rule-name=\"None\" dst-nat-rule-name=\"None\" protocol-id=\"6\" policy-name=\"123\" source-zone-name=\"TEST1\" destination-zone-name=\"TEST2\" session-id-32=\"14285714\" username=\"N/A\" roles=\"N/A\" packet-incoming-interface=\"reth1.100\"]")
    message = mt.render(mark="<23>1", host=host)

    sendsingle(message)

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"juniper:junos:firewall:structured\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


