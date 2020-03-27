# Vendor - Schneider


## Product - APC Power systems


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                  |
| Product Manual | multiple |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| apc:syslog  | None |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| schneider_apc      | apc:syslog     | main          | none          |

### Filter type

Port or IP based filter is required

### Setup and Configuration



### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_SCHNEIDER_APC_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_SCHNEIDER_APC_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_SCHNEIDER_APC | no | Enable archive to disk for this specific source |
| SC4S_DEST_SCHNEIDER_APC_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=apc:syslog | stats count by host
```
