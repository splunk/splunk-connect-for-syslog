# Vendor - Wallix

## Product - Bastion

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3661/                                                                 |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| WB:syslog  | note this sourcetype includes program:rdproxy all other data will be treated as nix  |


### Sourcetype and Index Configuration

| key                 | sourcetype             | index    | notes   |
|---------------------|------------------------|----------|---------|
| WB:syslog      | infraops      | main     | none    |

### Filter type

MSG Parse: This filter parses message content


| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_WALLIX_PROXY_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_WALLIX_PROXY_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_WALLIX_PROXY | no | Enable archive to disk for this specific source |
| SC4S_DEST_WALLIX_PROXY_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=WB:* | stats count by host
```

