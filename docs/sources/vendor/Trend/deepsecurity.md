# Deep Security

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://splunkbase.splunk.com/app/1936/>                                                            |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| deepsecurity-system_events        |                                                                                                |
| deepsecurity-intrusion_prevention        |                                                                                                |
| deepsecurity-integrity_monitoring        |                                                                                                |
| deepsecurity-log_inspection        |                                                                                                |
| deepsecurity-web_reputation        |                                                                                                |
| deepsecurity-firewall        |                                                                                                |
| deepsecurity-antimalware        |                                                                                                |
| deepsecurity-app_control        |                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
|Trend Micro_Deep Security Agent|deepsecurity|epintel|Used only if a correct source type is not matched|
|Trend Micro_Deep Security Agent_intrusion prevention|deepsecurity-intrusion_prevention|epintel||
|Trend Micro_Deep Security Agent_integrity monitoring|deepsecurity-integrity_monitoring|epintel||
|Trend Micro_Deep Security Agent_log inspection|deepsecurity-log_inspection|epintel||
|Trend Micro_Deep Security Agent_web reputation|deepsecurity-web_reputation|epintel||
|Trend Micro_Deep Security Agent_firewall|deepsecurity-firewall|epintel||
|Trend Micro_Deep Security Agent_antimalware|deepsecurity-antimalware|epintel||
|Trend Micro_Deep Security Agent_app control|deepsecurity-app_control|epintel||
|Trend Micro_Deep Security Manager|deepsecurity-system_events|epintel||

