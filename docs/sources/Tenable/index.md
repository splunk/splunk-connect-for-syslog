# Vendor - Tenable


## Product - Tenable.nnm

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4060/                                                                 |
| Product Manual | https://docs.tenable.com/integrations/Splunk/Content/Splunk2/ProcessWorkflow.htm                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| tenable:nnm:vuln        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| tenable_nnm      | enable:nnm:vuln       | netfw          | none          |

### Filter type

MSG Parsing

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_TENABLE_SYSLOG_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_TENABLE_SYSLOG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_TENABLE_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_TENABLE_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=enable:nnm:vuln | stats count by host
```