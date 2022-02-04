# Vendor - Arista


## Product - EOS Switch

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| arista:eos:*        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| arista_eos      | arista:eos       | netops          | none          |
| arista_eos_$PROCESSNAME      | arista:eos       | netops          | The "process" field is used from the event          |

### Filter type

MSG Parsing

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_ARISTA_EOS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_ARISTA_EOS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_ARISTA_EOS | no | Enable archive to disk for this specific source |
| SC4S_DEST_ARISTA_EOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=arista:eos:* | stats count by host
```
