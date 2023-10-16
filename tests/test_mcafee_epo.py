# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

mcafee_endpoint_security_testdata = [
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@3401 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] ?<?xml version="1.0" encoding="UTF-8"?><EPOEvent><MachineInfo><MachineName>DESKTOP-00001</MachineName><AgentGUID>0011aacc-eeee-0000-0000-000011223311</AgentGUID><IPAddress>10.222.22.131</IPAddress><OSName>Windows 10 Server</OSName><UserName>%CTX_DOMAIN_USER%</UserName><TimeZoneBias>-330</TimeZoneBias><RawMACAddress>000011223311</RawMACAddress></MachineInfo><SoftwareInfo ProductName="McAfee Endpoint Security" ProductVersion="10.6.1.1607" ProductFamily="TVD"><CommonFields><Analyzer>ENDP_GS_1060</Analyzer><AnalyzerName>McAfee Endpoint Security</AnalyzerName><AnalyzerVersion>10.6.1.1607</AnalyzerVersion><AnalyzerHostName>DESKTOP-00001</AnalyzerHostName><AnalyzerDATVersion></AnalyzerDATVersion><AnalyzerEngineVersion></AnalyzerEngineVersion></CommonFields><Event><EventID>1120</EventID><Severity>0</Severity><GMTTime>{{ iso }}</GMTTime><CommonFields><AnalyzerDetectionMethod></AnalyzerDetectionMethod><ThreatName>_</ThreatName><ThreatType></ThreatType><ThreatCategory>ops.update</ThreatCategory><ThreatHandled>1</ThreatHandled><ThreatActionTaken>none</ThreatActionTaken><ThreatSeverity>6</ThreatSeverity></CommonFields></Event></SoftwareInfo></EPOEvent>',
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@3401 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] ?<?xml version="1.0" encoding="UTF-8"?><EPOEvent><MachineInfo><MachineName>DESKTOP-00001</MachineName><AgentGUID>0011aacc-eeee-0000-0000-000011223311</AgentGUID><IPAddress>10.222.22.83</IPAddress><OSName>Windows 10 Server</OSName><UserName>%CTX_DOMAIN_USER%</UserName><TimeZoneBias>-330</TimeZoneBias><RawMACAddress>000011223311</RawMACAddress></MachineInfo><SoftwareInfo ProductName="McAfee Endpoint Security" ProductVersion="10.7.0.1285" ProductFamily="TVD"><CommonFields><Analyzer>ENDP_GS_1070</Analyzer><AnalyzerName>McAfee Endpoint Security</AnalyzerName><AnalyzerVersion>10.7.0.1285</AnalyzerVersion><AnalyzerHostName>DESKTOP-00001</AnalyzerHostName><AnalyzerDATVersion></AnalyzerDATVersion><AnalyzerEngineVersion></AnalyzerEngineVersion></CommonFields><Event><EventID>1118</EventID><Severity>0</Severity><GMTTime>{{ iso }}</GMTTime><CommonFields><AnalyzerDetectionMethod></AnalyzerDetectionMethod><ThreatName>_</ThreatName><ThreatType></ThreatType><ThreatCategory>ops.update.end</ThreatCategory><ThreatHandled>1</ThreatHandled><ThreatActionTaken>none</ThreatActionTaken><ThreatSeverity>6</ThreatSeverity></CommonFields></Event></SoftwareInfo></EPOEvent>',
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@3401 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] ?<?xml version="1.0" encoding="UTF-8"?><EPOevent><MachineInfo><MachineName>DESKTOP-00001</MachineName><AgentGUID>0011aacc-eeee-0000-0000-000011223311</AgentGUID><IPAddress>10.222.22.45</IPAddress><OSName>Windows 10 Workstation</OSName><UserName>SYSTEM</UserName><TimeZoneBias>-330</TimeZoneBias><RawMACAddress>000011223311</RawMACAddress></MachineInfo><SoftwareInfo ProductName="McAfee Endpoint Security" ProductVersion="10.6.1" ProductFamily="TVD"><CommonFields><Analyzer>ENDP_WP_1060</Analyzer><AnalyzerName>McAfee Endpoint Security</AnalyzerName><AnalyzerVersion>10.6.1</AnalyzerVersion><AnalyzerHostName>DESKTOP-00001</AnalyzerHostName><AnalyzerDetectionMethod>URL navigation</AnalyzerDetectionMethod></CommonFields><Event><EventID>18600</EventID><Severity>3</Severity><GMTTime>{{ iso }}</GMTTime><CommonFields><ThreatCategory>wp.detect.url</ThreatCategory><ThreatEventID>18600</ThreatEventID><ThreatSeverity>2</ThreatSeverity><ThreatName>Web Control Violation</ThreatName><ThreatType>IDS_THREAT_TYPE_URL</ThreatType><DetectedUTC>{{ iso }}Z</DetectedUTC><ThreatActionTaken>blocked</ThreatActionTaken><ThreatHandled>True</ThreatHandled><SourceIPV4>213.211.198.58</SourceIPV4><SourceURL>http://2222.aaaaa.org/download/eicarcom2.zip</SourceURL><SourceUserName>DESKTOP-00001\admin</SourceUserName><SourceProcessName>C:\Program Files\McAfee\Endpoint Security\Web Control\McChHost.exe</SourceProcessName><TargetUserName>DESKTOP-00001\admin</TargetUserName></CommonFields><CustomFields target="EPExtendedEventMT"><BladeName>IDS_BLADE_NAME_WP</BladeName><AnalyzerGTIQuery>True</AnalyzerGTIQuery><SourceProcessHash>03e33bcdd99853ea8c83407c3ab4599c</SourceProcessHash><SourceParentProcessName>C:\Program Files\Google\Chrome\Application\chrome.exe</SourceParentProcessName><SourceParentProcessHash>a1902e39f3a1610751b707a6742082c3</SourceParentProcessHash><SourceParentProcessSigned>True</SourceParentProcessSigned><SourceParentProcessSigner>Google LLC</SourceParentProcessSigner><SourceFileSize>0</SourceFileSize><SourceSigned>False</SourceSigned><SourceURLRatingCode>IDS_SECUIRTY_RATING_SA_RED</SourceURLRatingCode><SourceURLWebCategory>IDS_SAE_CONTENT_MS</SourceURLWebCategory><AttackVectorType>1</AttackVectorType><NaturalLangDescription>IDS_WC_NLD_URL_RATING|SourceURL=http://2222.aaaaa.org/download/eicarcom2.zip|SourceProcessName=C:\Program Files\McAfee\Endpoint Security\Web Control\McChHost.exe|SourceUserName=DESKTOP-00001\admin|ThreatActionTaken=blocked|AnalyzerName=McAfee Endpoint Security|SourceURLRatingCode=IDS_SECUIRTY_RATING_SA_RED</NaturalLangDescription></CustomFields><CustomFields target="WP_EventInfoMT"><EventTypeId>18600</EventTypeId><DomainName>2222.aaaaa.org</DomainName><URL>http://2222.aaaaa.org/download/eicarcom2.zip</URL><Count>1</Count><ObserverMode>0</ObserverMode><ActionID>4</ActionID><ReasonID>1</ReasonID><RatingID>3</RatingID><ListID>1</ListID><PhishingRatingID>4</PhishingRatingID><DownloadRatingID>3</DownloadRatingID><SpamRatingID>4</SpamRatingID><PopupRatingID>4</PopupRatingID><BadLinkRatingID>4</BadLinkRatingID><ExploitRatingID>4</ExploitRatingID><ContentID>130</ContentID><ContentCategories>00000100000000000000000011000000</ContentCategories></CustomFields></Event></SoftwareInfo></EPOevent>',
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@3401 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] ?<?xml version="1.0" encoding="UTF-8"?><EPOevent><MachineInfo><MachineName>DESKTOP-00001</MachineName><AgentGUID>0011aacc-eeee-0000-0000-000011223311</AgentGUID><IPAddress>10.222.22.131</IPAddress><OSName>Windows 10 Server</OSName><UserName>SYSTEM</UserName><TimeZoneBias>-330</TimeZoneBias><RawMACAddress>000011223311</RawMACAddress></MachineInfo><SoftwareInfo ProductName="McAfee Endpoint Security" ProductVersion="10.6.1" ProductFamily="TVD"><CommonFields><Analyzer>ENDP_AM_1060</Analyzer><AnalyzerName>McAfee Endpoint Security</AnalyzerName><AnalyzerVersion>10.6.1</AnalyzerVersion><AnalyzerHostName>DESKTOP-00001</AnalyzerHostName><AnalyzerEngineVersion>6010.8670</AnalyzerEngineVersion><AnalyzerDetectionMethod>On-Access Scan</AnalyzerDetectionMethod><AnalyzerDATVersion>3811.0</AnalyzerDATVersion></CommonFields><Event><EventID>1278</EventID><Severity>3</Severity><GMTTime>{{ iso }}</GMTTime><CommonFields><ThreatCategory>av.detect</ThreatCategory><ThreatEventID>1278</ThreatEventID><ThreatSeverity>2</ThreatSeverity><ThreatName>EICAR test file</ThreatName><ThreatType>test</ThreatType><DetectedUTC>{{ iso }}Z</DetectedUTC><ThreatActionTaken>IDS_ALERT_ACT_TAK_DEL</ThreatActionTaken><ThreatHandled>True</ThreatHandled><SourceHostName>DESKTOP-00001</SourceHostName><SourceProcessName>C:\Users\admin123.WIN-QFN79SPC5U4.000\Desktop\Tops.exe</SourceProcessName><TargetHostName>DESKTOP-00001</TargetHostName><TargetUserName>DESKTOP-00001\admin123</TargetUserName><TargetFileName>C:\Users\admin123.WIN-QFN79SPC5U4.000\Desktop\TEST_SAMPLES_MVS\Standard Test Set\eicar</TargetFileName></CommonFields><CustomFields target="EPExtendedEventMT"><BladeName>IDS_BLADE_NAME_SPB</BladeName><AnalyzerContentCreationDate>2019-08-25T02:22:00Z</AnalyzerContentCreationDate><AnalyzerGTIQuery>False</AnalyzerGTIQuery><ThreatDetectedOnCreation>True</ThreatDetectedOnCreation><TargetName>eicar</TargetName><TargetPath>C:\Users\admin123.WIN-QFN79SPC5U4.000\Desktop\TEST_SAMPLES_MVS\Standard Test Set</TargetPath><TargetHash>e7e5fa40569514ec442bbdf755d89c2f</TargetHash><TargetFileSize>70</TargetFileSize><TargetModifyTime>2000-10-24T05:13:46Z</TargetModifyTime><TargetAccessTime>2019-08-26T05:32:39Z</TargetAccessTime><TargetCreateTime>2019-08-26T05:32:39Z</TargetCreateTime><Cleanable>False</Cleanable><TaskName>IDS_OAS_TASK_NAME</TaskName><FirstAttemptedAction>IDS_ALERT_THACT_ATT_CLE</FirstAttemptedAction><FirstActionStatus>False</FirstActionStatus><SecondAttemptedAction>IDS_ALERT_THACT_ATT_DEL</SecondAttemptedAction><SecondActionStatus>True</SecondActionStatus><AttackVectorType>4</AttackVectorType><DurationBeforeDetection>10</DurationBeforeDetection><NaturalLangDescription>IDS_NATURAL_LANG_OAS_DETECTION_DEL|TargetName=eicar|TargetPath=C:\Users\admin123.WIN-QFN79SPC5U4.000\Desktop\TEST_SAMPLES_MVS\Standard Test Set|ThreatName=EICAR test file|SourceProcessName=C:\Users\admin123.WIN-QFN79SPC5U4.000\Desktop\Tops.exe|ThreatType=test|TargetUserName=DESKTOP-00001\admin123</NaturalLangDescription><AccessRequested></AccessRequested><DetectionMessage>IDS_OAS_DEFAULT_THREAT_MESSAGE</DetectionMessage><AMCoreContentVersion>3811.0</AMCoreContentVersion></CustomFields></Event></SoftwareInfo></EPOevent>',
]
mcafee_agent_testdata = [
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@4444 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] <?xml version="1.0" encoding="utf-8"?><UpdateEvents><MachineInfo><AgentGUID>{0011aacc-eeee-0000-0000-000011223311}</AgentGUID><MachineName>THEMBP1</MachineName><RawMACAddress>000011223311</RawMACAddress><IPAddress>172.16.23.123</IPAddress><AgentVersion>1.1.1.103</AgentVersion><OSName>Windows 10</OSName><TimeZoneBias>240</TimeZoneBias><UserName></UserName></MachineInfo><McAfeeCommonUpdater ProductName="McAfee Agent" ProductVersion="1.0.0" ProductFamily="TVD"><UpdateEvent><EventID>2422</EventID><Severity>4</Severity><GMTTime>{{ iso }}</GMTTime><ProductID>POLICYAU6000</ProductID><Locale>0409</Locale><Error>59</Error><Type>Policy Enforcement</Type><Version>N/A</Version><InitiatorID>EPOAGENT3000</InitiatorID><InitiatorType>N/A</InitiatorType><SiteName>N/A</SiteName><Description>N/A</Description></UpdateEvent></McAfeeCommonUpdater></UpdateEvents>',
]
policy_auditor_vulnerability_assessment_testdata = [
    r'{{ mark }} {{ iso }}Z {{ host }} EPOEvents - EventFwd [agentInfo@4444 tenantId="1" bpsId="1" tenantGUID="{00000000-0000-0000-0000-000000000000}" tenantNodePath="1\2"] <?xml version="1.0" encoding="utf-8"?><AssessmentResultEvent><MachineInfo><AgentGUID>{0011aacc-eeee-0000-0000-000011223311}</AgentGUID><MachineName>THEMBP1</MachineName><RawMACAddress>000011223311</RawMACAddress><IPAddress>172.16.23.123</IPAddress><AgentVersion>1.1.1.103</AgentVersion><OSName>Linux</OSName><TimeZoneBias>0</TimeZoneBias><UserName>GARY</UserName></MachineInfo><PhoenixEngine ProductName="Policy Auditor Vulnerability Assessment" ProductVersion="1.1.0" ProductFamily="Security" EngineVersion="1.1.0"><InventoryAssessmentResultInfo><EventID>18905</EventID><Severity>0</Severity><GMTTime>{{ iso }}</GMTTime><ProductName>Policy Auditor Vulnerability Assessment</ProductName><ProductVersion>1.1.0</ProductVersion><ProductFamily>Security</ProductFamily><EngineVersion>0</EngineVersion><TaskId>20</TaskId><Result>eJx1jjELgzAUhPf+ipCpBYWoS+smOHYQHEuR1xjKK+YZzEupiP+9j+7d7o7vuNs0gXe61l2jmhgd qxYYVG+BCOmprkjpo45N1/UnnemUcBS4NKIZvYsMPvyC0uSmyouLKqramLo8C7G4mCYeeA2ysGkI YUILjDMN8+PlLEsTyS7OO2KY9J6JfYuel3UY5ce/1u2+74cvff89lg==</Result></InventoryAssessmentResultInfo></PhoenixEngine></AssessmentResultEvent>',
]


@pytest.mark.parametrize("event", mcafee_endpoint_security_testdata)
@pytest.mark.addons("mcafee")
def test_mcafee_epo_structured_mcafee_endpoint_security(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="mcafee:epo:syslog" source="mcafee_endpoint_security"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", mcafee_agent_testdata)
@pytest.mark.addons("mcafee")
def test_mcafee_epo_structured_mcafee_agent(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="mcafee:epo:syslog" source="mcafee_agent"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.parametrize("event", policy_auditor_vulnerability_assessment_testdata)
@pytest.mark.addons("mcafee")
def test_mcafee_epo_structured_policy_auditor_vulnerability_assessment(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="mcafee:epo:syslog" source="policy_auditor_vulnerability_assessment"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
