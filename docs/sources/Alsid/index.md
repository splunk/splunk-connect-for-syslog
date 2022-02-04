# Vendor - Alsid Replaced by Tenable AD


## Product - AD

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/5173/                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| alsid:syslog        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| alsid_syslog      | alsid:syslog       | oswinsec          | none          |

### Filter type

MSG Parsing

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_ALSID_SYSLOG_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_ALSID_SYSLOG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_ALSID_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_ALSID_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=alsid:syslog | stats count by host
```
