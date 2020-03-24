# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *
import pytest

env = Environment()
testdata = [
    '{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@4444 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] <?xml version="1.0" encoding="utf-8"?><UpdateEvents><MachineInfo><AgentGUID>{0011aacc-eeee-0000-0000-000011223311}</AgentGUID><MachineName>THEMBP1</MachineName><RawMACAddress>000011223311</RawMACAddress><IPAddress>172.16.23.123</IPAddress><AgentVersion>1.1.1.103</AgentVersion><OSName>Windows 10</OSName><TimeZoneBias>240</TimeZoneBias><UserName></UserName></MachineInfo><McAfeeCommonUpdater ProductName="McAfee Agent" ProductVersion="1.0.0" ProductFamily="TVD"><UpdateEvent><EventID>2422</EventID><Severity>4</Severity><GMTTime>{{ iso }}</GMTTime><ProductID>POLICYAU6000</ProductID><Locale>0409</Locale><Error>59</Error><Type>Policy Enforcement</Type><Version>N/A</Version><InitiatorID>EPOAGENT3000</InitiatorID><InitiatorType>N/A</InitiatorType><SiteName>N/A</SiteName><Description>N/A</Description></UpdateEvent></McAfeeCommonUpdater></UpdateEvents>\n',
    '{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@4444 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] <?xml version="1.0" encoding="utf-8"?><AssessmentResultEvent><MachineInfo><AgentGUID>{0011aacc-eeee-0000-0000-000011223311}</AgentGUID><MachineName>THEMBP1</MachineName><RawMACAddress>000011223311</RawMACAddress><IPAddress>172.16.23.123</IPAddress><AgentVersion>1.1.1.103</AgentVersion><OSName>Linux</OSName><TimeZoneBias>0</TimeZoneBias><UserName>GARY</UserName></MachineInfo><PhoenixEngine ProductName="Policy Auditor Vulnerability Assessment" ProductVersion="1.1.0" ProductFamily="Security" EngineVersion="1.1.0"><InventoryAssessmentResultInfo><EventID>18905</EventID><Severity>0</Severity><GMTTime>{{ iso }}</GMTTime><ProductName>Policy Auditor Vulnerability Assessment</ProductName><ProductVersion>1.1.0</ProductVersion><ProductFamily>Security</ProductFamily><EngineVersion>0</EngineVersion><TaskId>20</TaskId><Result>eJx1jjELgzAUhPf+ipCpBYWoS+smOHYQHEuR1xjKK+YZzEupiP+9j+7d7o7vuNs0gXe61l2jmhgd qxYYVG+BCOmprkjpo45N1/UnnemUcBS4NKIZvYsMPvyC0uSmyouLKqramLo8C7G4mCYeeA2ysGkI YUILjDMN8+PlLEsTyS7OO2KY9J6JfYuel3UY5ce/1u2+74cvff89lg==</Result></InventoryAssessmentResultInfo></PhoenixEngine></AssessmentResultEvent>\n'
]
@pytest.mark.parametrize("event", testdata)
def test_mcafee_epo_structured(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s,event):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event)
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=epav host=\"{{ host }}\" sourcetype=\"mcafee:epo:syslog\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
