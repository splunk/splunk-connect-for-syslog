# Vendor - Netmotion


## Product - Reporting


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                  |
| Product Manual | unknown |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| netmotion:reporting  | None |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| netmotion_reporting      | netmotion:reporting     | netops          | none          |

### Filter type

MSG Parsing

### Setup and Configuration



### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_NETMOTION_REPORTING_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_NETMOTION_REPORTING_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_NETMOTION_REPORTING | no | Enable archive to disk for this specific source |
| SC4S_DEST_NETMOTION_REPORTING_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=netmotion:reporting | stats count by host
```
