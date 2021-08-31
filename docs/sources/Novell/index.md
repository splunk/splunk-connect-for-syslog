# Vendor - Novell

## Product - NetIQ

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                               |
| Product Manual | unknown |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| novell:netiq     |  none  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| novell_netiq    | novell_netiq    | netauth          | None     |

### Filter type

MSGParser


### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_NOVELL_NETIQ_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_NOVELL_NETIQ_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_NOVELL_NETIQ | no | Enable archive to disk for this specific source |
| SC4S_DEST_NOVELL_NETIQ_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=netauth sourcetype=novel:netiq
```

Verify timestamp, and host values match as expected