# Vendor - Brocade


## Product - Switches

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| brocade:syslog        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| brocade_syslog      | brocade:syslog       | netops          | none          |

### Filter type

Must be identified by host or ip assignment. Update the filter `f_brocade_syslog` or configure a dedicated port as required

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_BROCADE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_BROCADE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_BROCADE | no | Enable archive to disk for this specific source |
| SC4S_DEST_BROCADE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=brocade:syslog| stats count by host
```
