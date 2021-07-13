# Vendor - Dell

## Product - EPV

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                            |
| Add-on Manual | https://www.dell.com/support/manuals/en-au/dell-opnmang-sw-v8.1/eemi_13g_v1.2-v1/introduction?guid=guid-8f22a1a9-ac01-43d1-a9d2-390ca6708d5e&lang=en-us                                                    |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:poweredge:idrac:syslog        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_poweredge_idrac      | dell:poweredge:idrac:syslog     | infraops          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_DELL_POWEREDGE_IDRAC_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_DELL_POWEREDGE_IDRAC_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |


### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef sourcetype="UDP")
```
