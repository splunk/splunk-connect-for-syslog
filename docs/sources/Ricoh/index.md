# Vendor - Ricoh


## Product - MFP

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ricoh:mfp        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ricoh_syslog      | ricoh:mfp       | printer          | none          |

### Filter type

MSG Parsing

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_RICOH_SYSLOG_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_RICOH_SYSLOG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_RICOH_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_RICOH_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_SOURCE_RICOH_SYSLOG_FIXHOST | yes | Current firmware incorrectly sends the value of HOST in the program field if this is ever corrected this value will need to be set back to no we suggest using yes | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=alcatel:switch | stats count by host
```
