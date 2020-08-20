# Vendor - Tend

## Product - Deep Security

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | https://splunkbase.splunk.com/app/1936/                                                            |


### Sourcetypes

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

### Filter type

MSG Parse: This filter parses message content

### Options

Note listed for reference processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_CEF | no | Enable archive to disk for this specific source |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

* NOTE:  Set only _one_ set of CEF variables for the entire SC4S deployment, regardless of how
many ports are in use by this CEF source (or any others).  See the "Common Event Format" source
documentation for more information.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=<asconfigured> (sourcetype="deepsecurity*")
```
